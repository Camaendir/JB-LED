import time
import multiprocessing

class Engine:

    def __init__(self, pMQTT):
        self.isRunning = False
        self.brightness = 100
        self.subengines = []
        self.processes = []
        self.frames = {}
        self.controler = None

        if pMQTT:
            self.startMQTT()

    def startMQTT(self):
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.client.subscribe("strip/effekt/#")
        self.client.subscribe("strip/command")
        self.client.subscribe("strip/color/#")
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
            self.subengines.append(pSub)
            self.processes.append([pSub.mqttTopic, None, None, pIsEnabled, pSub.isCompressed])

    def run(self):
        try:
            self.isRunning = True
            self.controler.setup()

            while self.isRunning:
                fr = time.clock()
                frames = [[-1, -1, -1]] * self.controler.pixellength
                for row in self.processes:
                    if row[3] and row[2] == None and row[1] == None:
                        self.startSubEngine(row[0])
                    elif not row[3] and row[2] != None and row[1] != None:
                        self.terminateSubEngine(row[0])
                    elif row[3]:
                        frame = self.frames[row[0]]
                        if row[2].poll():
                            if row[4]:
                                frame = self.decompFrame(row[2].recv())
                            else:
                                frame = row[2].recv()
                            self.frames[row[0]] = frame
                            row[2].send("f")
                        for i in range(len(frames)):
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
        except:
            print("Error: in Engine")
            self.terminateAll()

    def bitToRow(self, pBits):
        retVal = [0, [0, 0, 0]]
        retVal[0] = (pBits & 4278190080) >> 24
        if retVal[0] == 255:
            retVal[0] = pBits & 255
            retVal[1] = [-1,-1,-1]
        else:
            retVal[1][0] = (pBits & 16711680) >> 16
            retVal[1][1] = (pBits & 65280) >> 8
            retVal[1][2] = pBits & 255
        return retVal

    def decompFrame(self, pFrame):
        block = []
        for data in pFrame:
            block.append(self.bitToRow(data))
        retVal = []
        for row in block:
            retVal = retVal + [row[1]]*(row[0]+1)
        return retVal

    def startSubEngine(self, pMqttTopic):
        if self.isRunning: #[pSub.mqttTopic, process, parent, True]
            newSub = None
            for sub in self.subengines:
                if sub.mqttTopic == pMqttTopic:
                    newSub = sub
                    break
            if newSub == None:
                return
            parent, child = multiprocessing.Pipe()
            process = multiprocessing.Process(target=newSub.run)
            newSub.configur(child)
            for row in self.processes:
                if row[0] == pMqttTopic:
                    row[1] = process
                    row[2] = parent
                    row[3] = True
                    break
            process.start()
            self.frames[pMqttTopic] = ([[-1, -1, -1]]*450)

    def terminateSubEngine(self, pMqttTopic):
        for row in self.processes:
            if row[0] == pMqttTopic:
                print("Terminate: "+pMqttTopic)
                row[2].send("t")
                print("Joining Process...")
                row[1].join()
                print("Done!")
                row[2].close()
                row[1] = None
                row[2] = None
                row[3] = False

    def terminateAll(self):
        for row in self.processes:
            print("Terminate Process...")
            row[2].send("t")

        for row in self.processes:
            print("Join Process...")
            row[1].join()
            row[2].close()
            row[1] = None
            row[2] = None
        print("Done!")

if __name__ == '__main__':
    from Lib.Controler.TestControler import TestControler
    print("Test")
    eng = Engine(False)
    eng.setControler(TestControler())
    eng.run()

