import time
import multiprocessing
from Lib.Compression import decompFrame
from Lib.Effects.Alarm import Alarm

class ProcessWrap:

    def __init__(self, pSub, pIsEnabled):
        self.mqttTopic = pSub.mqttTopic
        self.subEngine = pSub
        self.process = None
        self.pipe = None
        self.isAcknowledged = True
        self.isEnabled = pIsEnabled
        self.isCompressed = pSub.isCompressed
        self.compClass = pSub.compClass

    def isActive(self):
        return self.pipe != None and self.process != None

    def reset(self):
        if self.isActive():
            self.pipe.close()
            self.pipe = None
            self.process = None
        self.isAcknowledged = True
        self.isEnabled = False

class Engine:

    def __init__(self):
        self.isRunning = False
        self.brightness = 100
        self.processes = []
        self.frames = {}
        self.controler = None
        self.pixellength = 0

    def startMQTT(self,pName):
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.subscribe(pName+ "/effekt/#")
        self.client.subscribe(pName+ "/command")
        self.client.subscribe(pName+ "/color/#")
        self.client.loop_start()

    def setControler(self, pControler):
        self.controler = pControler

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        print([msg.topic, msg.payload])
        if topic == "strip/command":
            if msg.payload == "update":
                pass
            elif msg.payload == "reset":
                self.pixels.blackout()
        elif topic.startswith("strip/color/"):
            topic = topic[12:]
            if topic == "brightnis":
                self.brightness = int(msg.payload)
        elif topic.startswith("strip/effekt/"):
            topic = topic[13:]
            for row in self.processes:
                if topic.startswith(row[0]+"/"):
                    topic = topic[len(row[0])+1:]
                    if topic == "enable":
                        row[3] = msg.payload.lower() in ("true", "t", "1", "on")
                    elif row[2] != None:
                        row[2].send("m:"+topic+"/"+msg.payload)

    def addSubEngine(self, pSub, pIsEnabled):
        if not self.isRunning:
            self.processes.append(ProcessWrap(pSub, pIsEnabled))

    def run(self):
        try:
            self.isRunning = True
            self.controler.setup()
            self.pixellength = self.controler.pixellength

            while self.isRunning:
                fr = time.clock()
                frames = [[-1, -1, -1]] * self.pixellength
                for wrap in self.processes:
                    if wrap.isEnabled and wrap.isAcknowledged and wrap.isActive():
                        wrap.pipe.send("f")
                for wrap in self.processes:
                    if wrap.isEnabled and not wrap.isActive():
                        self.startSubEngine(wrap)
                    elif not wrap.isEnabled and wrap.isActive():
                        self.terminateSubEngine(wrap)
                    elif wrap.isEnabled:
                        frame = self.frames[wrap.mqttTopic]

                        buff = []
                        while wrap.pipe.poll():
                            buff.append(wrap.pipe.recv())
                            wrap.isAcknowledged = True

                        if len(buff)>0:
                            if wrap.isCompressed:
                                frame = wrap.compClass.decompress(buff.pop(len(buff) - 1))
                            else:
                                frame = buff.pop(len(buff) - 1)
                            self.frames[wrap.mqttTopic] = frame
                        for i in range(min(len(frame),len(frames), self.pixellength)):
                            if frames[i] == [-1, -1, -1]:
                                frames[i] = frame[i]
                brPercent = float(self.brightness) / 100
                completeFrame = []
                for i in range(len(frames)):
                    color = []
                    for a in frames[i]:
                        color.append(int(max(0, a) * brPercent))
                    completeFrame.append(color)

                self.controler.setFrame(completeFrame)

                fr = time.clock() - fr
                if fr <= 0.02:
                    time.sleep(0.02 - fr)

        except KeyboardInterrupt:
            self.terminateAll()
        except Exception as e:
            print("Error: in Engine")
            print(e)
            self.terminateAll()

    def startSubEngine(self, prWrap):
        if self.isRunning and not prWrap.isActive(): #[pSub.mqttTopic, process, parent, True]
            parent, child = multiprocessing.Pipe()
            process = multiprocessing.Process(target=prWrap.subEngine.run)
            prWrap.subEngine.configur(child, self.pixellength)
            prWrap.process = process
            prWrap.pipe = parent
            prWrap.isEnabled = True
            process.start()
            print("Started: " + prWrap.mqttTopic)
            self.frames[prWrap.mqttTopic] = ([[-1, -1, -1]]*self.pixellength)

    def terminateSubEngine(self, prWrap):
        if prWrap.isActive():
            print("Terminate: " + prWrap.mqttTopic)
            prWrap.pipe.send("t")
            print("Joining Process...")
            prWrap.process.join()
            print("Done!")
            prWrap.pipe.close()
            prWrap.process = None
            prWrap.pipe = None
            prWrap.isEnabled = False


    def terminateAll(self):
        self.isRunning = False
        for wrap in self.processes:
            self.terminateSubEngine(wrap)