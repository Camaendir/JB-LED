from time import clock, sleep
from neopixel import *

import paho.mqtt.client as mqtt
from Resources import *

transparent = [-1, -1, -1]

class Engine:

    def __init__(self, pPixellength=450):
        self.isRunning = False #MultiThreading
        self.daemon = True

        self.pixels = Strip() #Strip
        self.brightnis = 100
        self.pixellength = pPixellength

        self.subengines = []
        self.framebuffer = FrameBuffer()
        self.resources = {
            "MusicAdapter": MusicAdapter()
        }

        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.subscribe("strip/effekt/#")
        self.client.subscribe("strip/command")
        self.client.subscribe("strip/color/#")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        print([msg.topic, msg.payload])
        if topic == "strip/command":
            if msg.payload == "update":
                self.publishState()
            elif msg.payload == "reset":
                self.pixels.blackout()
        elif topic.startswith("strip/color/"):
            topic = topic[12:]
            if topic == "brightnis":
                self.brightnis = int(msg.payload)
        elif topic.startswith("strip/effekt/"):
            topic = topic[13:]
            for subengine in self.subengines:
                if topic.startswith(subengine.mqttTopic + "/"):
                    t = topic[len(subengine.mqttTopic) + 1:]
                    subengine.on_message(t, msg.payload)

    def publishState(self):
        self.client.publish(topic="strip/info/color/brightnis", payload=self.brightnis)
        for subengine in self.subengines:
            tp = subengine.getStates()
            for subj in tp:
                self.client.publish(topic=subj[0], payload=subj[1])

    def addSubEngine(self, pSubEngine):
        if not self.isRunning:
            pSubEngine.configur(self.framebuffer, len(self.subengines), self.pixellength)
            self.subengines.append(pSubEngine)
            print("SE added")

    def getResources(self):
        return self.resources

    def terminate(self):
        self.isRunning = False
        self.join()

        for r in self.resources:
            self.resources[r].terminate()

    def run(self):
        self.isRunning = True
        self.pixels.create()
        self.pixels.blackout()

        lastpixel = [[0,0,0]]*self.pixellength
        while self.isRunning:            
            for se in self.subengines:
                if se.isEnabled:
                    se.getFrame()

            #process Join

            #Buffer readout
            bufferFrames = self.framebuffer.getBuffer()
            
            frame = [[-1, -1, -1]] * self.pixellength
            for sub_frame in bufferFrames:
                index = 0
                for pixel in sub_frame:
                    if -1 not in pixel:
                        frame[index] = pixel
                    index = index + 1

            #Push pixel to LED Strip
            bri = float(self.brightnis) / 100
            index = 0
            for pixelcolor in frame:
                for rgb in range(len(pixelcolor)):
                    pixelcolor[rgb] = max(pixelcolor[rgb], 0)

                if pixelcolor is not lastpixel[index]:
                    cl = []
                    for i in pixelcolor:
                        
                        cl.append(int(bri * i))
                    self.pixels.setPixel(index, color=cl)

                index = index + 1
            self.pixels.show()
            


#Checked Modul
class FrameBuffer:
    def __init__(self):
        self.frameBuffer = []
        self.waitperiod = 0.001
        sleep(self.waitperiod)
        self.isWritable = True

    def writeFrame(self, pSubeEngine, pFrame):
        if self.isWritable:
            self.frameBuffer.append([pSubeEngine, pFrame])
            return True
        return False

    def reset(self):
        self.isWritable = False
        sleep(self.waitperiod)
        self.frameBuffer = []
        self.isWritable = True

    def getBuffer(self):
        self.isWritable = False
        sleep(self.waitperiod)
        sort = self.frameBuffer[:]
        self.frameBuffer = []
        self.isWritable = True

        sorted = [sort.pop(0)]
        for look in sort:
            for i in range(len(sorted)):
                if look[0] < sorted[i][0]:
                    sorted.insert(i, look)
                    break
                if i + 1 == len(sorted):
                    sorted.append(look)
        retVal = []
        for tmp in sorted:
            retVal.append(tmp[1])
        return retVal



class SubEngine: #update() onMessage(topic,payload) getStates()
    
    global transparent

    def build(self, mqtttopic, layercount):
        self.framebuffer = None
        self.index = -1
        self.pixellength = 0
        self.layList = []
        self.mqttTopic = mqtttopic
        self.isEnabled = False

        self.transparent = transparent
        

        for i in range(layercount):
            tmp = Layer()
            tmp.build()
            self.layList.append(tmp)

    def configur(self, pFrameBuffer, pIndex, pPixellength):
        self.framebuffer = pFrameBuffer
        self.index = pIndex
        self.pixellength = pPixellength

    def addObj(self, obj, layer=0):
        self.layList[layer].addObj(obj)

    def delObj(self, obj):
        for layer in self.layList:
            layer.delObj(obj)

    def getFrame(self):
        if self.framebuffer == None or self.index < 0 or self.pixellength <= 0:
            return

        self.update()

        plain = [self.transparent]*self.pixellength
        frames = []

        for layer in self.layList:
            frames.append(layer.getFrame())
        #print(frames)

        for i in range(len(frames)):
            for j in range(self.pixellength):
                if plain[j] == self.transparent and frames[i][j] != self.transparent:
                    plain[j] = frames[i][j]
        
        self.framebuffer.writeFrame(self.index, plain)

    def on_message(self, topic, payload):
        if topic == "enable":
            print([topic, payload])
            self.isEnabled = payload.lower() in ("true", "t", "1", "on")
        self.onMessage(topic, payload)

    def get_State(self):
        retVal = self.getStates()
        if type([])==type(retVal):
            retVal.append([["strip/info/"+self.mqttTopic+"/enable"], str(self.isEnabled)])
            return retVal
        return [["strip/info/"+self.mqttTopic+"/enable"], str(self.isEnabled)]


class Layer:
    
    global transparent

    def build(self, pixellength=450):
        self.objList = []
        self.pixellength = pixellength
        
    
    def addObj(self, obj):
        self.objList.append(obj)

    def delObj(self, obj):
        self.objList.remove(obj)

    def getFrame(self):
        field = [transparent]*self.pixellength
        
        for obj in self.objList:           
            if obj.isVisible:
                for i in range(len(obj.content)):
                    index = obj.position - i
                    if index < 0:
                        index = self.pixellength + index
                    field[index] = obj.content[i]
        #print(field)
        return field


class Row:

    def __init__(self):
        self.position = 0;
        self.isVisible = False
        self.content = []

        self.kernelContent = []

        self.isMirrowed = False
        self.isLooped = False
        self.isRepeated = False
        self.repeats = 0

    def setContent(self, pContent):
        self.kernelContent = pContent[:]
        self.processing()

    def stayMirrored(self, pBoolean):
        self.isMirrowed = pBoolean
        self.processing()

    def stayRepeated(self, pBoolean, pNum):
        if pNum > 0 and pBoolean:
            self.isRepeated = True
            self.repeats = pNum
        else:
            self.isRepeated = False
            self.repeats = 0
        self.processing()

    def stayLooped(self, pBoolean):
        self.isLooped = pBoolean
        self.processing()

    def shift(self, pixel=[-1, -1, -1]):
        lastPixel = self.kernelContent[len(self.kernelContent)-1]
        self.kernelContent.remove(lastPixel)
        if self.isLooped:
            self.kernelContent.insert(0, lastPixel)
        else:
            self.kernelContent.insert(0,pixel)

    def insert(self, index, pixel):
        self.kernelContent.insert(index, pixel)
        self.processing()

    def replace(self, index, pixel):
        self.kernelContent[index] = pixel
        self.processing()

    def processing(self):
        newContent = self.kernelContent[:]

        #Mirror
        if self.isMirrowed:
            for i in range(len(self.kernelContent) - 1, -1, -1):
                newContent.append(self.kernelContent[i])


        #Repeat
        if self.isRepeated:
            newContent = newContent * self.repeats

        #Push to Content
        self.content = newContent


class Strip:

    def __init__(self):
        self.PIN_1 = 13
        self.PIN_2 = 18
        self.FREQ = 1200000
        self.DMA_1 = 11
        self.DMA_2 = 10
        self.BRIGHTNES = 128
        self.INVERT = False
        self.CHANNEL_1 = 1
        self.CHANNEL_2 = 0
        self.strip1 = None
        self.strip2 = None

    def create(self, pixel1=245, pixel2=205):
        self.strip1 = Adafruit_NeoPixel(pixel1, self.PIN_1, self.FREQ, self.DMA_1, self.INVERT, self.BRIGHTNES,
                                        self.CHANNEL_1)
        self.strip2 = Adafruit_NeoPixel(pixel2, self.PIN_2, self.FREQ, self.DMA_2, self.INVERT, self.BRIGHTNES,
                                        self.CHANNEL_2)
        self.strip1.begin()
        self.strip2.begin()

    def show(self):
        self.strip1.show()
        self.strip2.show()

    def setPixel(self, pixel, r=0, g=0, b=0, color=None):
        if color is None:
            if (pixel < 245):
                self.strip1.setPixelColor(pixel, Color(g, r, b))
            else:
                self.strip2.setPixelColor(205 - (pixel - 244), Color(g, r, b))
        else:
            if (pixel < 245):
                self.strip1.setPixelColor(pixel, Color(color[1], color[0], color[2]))
            else:
                self.strip2.setPixelColor(205 - (pixel - 244), Color(color[1], color[0], color[2]))

    def fill(self, color):
        self.strip2.fill(color)
        self.strip1.fill(color)

    def test(self):
        for i in range(450):
            self.setPixel(i, 255, 0, 0)
            self.show()
        for i in range(450):
            self.setPixel(i, 0, 0, 0)
            self.show()

    def blackout(self):
        for i in range(450):
            self.setPixel(i, 0, 0, 0)
        self.show()


