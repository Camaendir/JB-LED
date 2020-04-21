import sys
import time
import multiprocessing

from BaseClasses.EngineProcess import EngineProcess
import paho.mqtt.client as mqtt


class Engine:

    def __init__(self):
        self.isRunning = False
        self.brightness = 100
        self.subengines = []
        self.processes = []
        self.frames = {}
        self.controller = None
        self.pixellength = 0
        self.mqtt_client = None
        self.pretopic = None

    def startMQTT(self, pretopic, host="localhost", port=1883, timeout=60):
        self.pretopic = pretopic
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(host, port, timeout)
        self.mqtt_client.subscribe(pretopic + "/effekt/#")
        self.mqtt_client.subscribe(pretopic + "/command")
        self.mqtt_client.subscribe(pretopic + "/color/#")
        self.mqtt_client.loop_start()

    def setControler(self, pControler):
        self.controller = pControler

    def on_message(self, client, userdata, msg):
        if not self.isRunning:
            print("Recieved MQTT message but could not be processed, because Engine is not running")
            return
        topic = msg.topic
        if topic == self.pretopic + "/command":  # Command
            self.on_command(msg.payload, None)

        elif topic.startswith(self.pretopic + "/color/"):  # Color change
            sub_topic = topic[len(self.pretopic) + 7:]
            if sub_topic == "brightness":
                self.brightness = int(msg.payload)

        elif topic.startswith(self.pretopic + "/effekt/"):  # Effect Command
            sub_topic = topic[len(self.pretopic) + 8:]
            for process in self.processes:
                if sub_topic.startswith(process.name + "/"):
                    effect_topic = sub_topic[len(process.name) + 1:]
                    if effect_topic == "enable":
                        process.isEnabled = msg.payload.lower() in ("true", "t", "1", "on")
                    elif process.parent is not None:
                        process.parent.send("m:" + effect_topic + "/" + msg.payload)

    def on_command(self, command, attributes):
        if command == "update":
            pass
        elif command == "reset":
            self.controller.setFrame([[0, 0, 0]] * self.pixellength)

    def addSubEngine(self, pSub, pIsEnabled):
        if not self.isRunning:
            self.subengines.append(pSub)
            self.processes.append(
                EngineProcess(pSub, pSub.mqttTopic, None, None, pIsEnabled, pSub.isCompressed, pSub.compressor)
            )
        else:
            print('Could not add SubEngine, because Engine is already running')

    def run(self):
        try:
            self.isRunning = True
            self.controller.setup()
            self.pixellength = self.controller.pixellength
            while self.isRunning:
                fr = time.clock()
                frames = [[-1, -1, -1]] * self.pixellength
                for process in self.processes:
                    if process.isEnabled and process.parent is not None and process.process is not None:
                        process.parent.send("f")
                for process in self.processes:
                    if process.isEnabled and process.parent is None and process.process is None:
                        self.startSubEngine(process.subengine)
                    elif not process.isEnabled and process.parent is not None and process.process is not None:
                        self.terminateSubEngine(process.subengine)
                    elif process.isEnabled:
                        frame = self.frames[process.name]
                        if process.parent.poll():
                            if process.isCompressed:
                                frame = process.compressor.decompressFrame(process.parent.recv())
                            else:
                                frame = process.parent.recv()
                            self.frames[process.name] = frame
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
                self.controller.setFrame(completeFrame)
                fr = time.clock() - fr
                if fr <= 0.02:
                    time.sleep(0.02 - fr)

        except KeyboardInterrupt:
            self.terminateAll()
        except:
            print("Unexpected Error in Engine:", sys.exc_info()[0])
            print("Terminating all SubEngines!")
            self.terminateAll()
            print("All SubEngines terminated.")
            print("Shutting down Engine.")

    def startSubEngine(self, engineProcess):
        if self.isRunning:
            if engineProcess.subengine.isRunning:
                print("Could not start SubEngine, because SubEngine is already running")
                return
            parent, child = multiprocessing.Pipe()
            process = multiprocessing.Process(target=engineProcess.subengine.run)
            engineProcess.subengine.configure(child)
            engineProcess.process = process
            engineProcess.parent = parent
            engineProcess.isEnabled = True
            process.start()
            self.frames[engineProcess.name] = ([[-1, -1, -1]] * self.pixellength)
        else:
            print("Could not start SubEngine, because Engine is not running")

    def terminateSubEngine(self, process):
        if not process.isEnabled:
            process.parent = None
            process.process = None
            return
        if process.parent is not None:
            print("Terminate Process... " + process.name)
            process.parent.send("t")
        if process.process is not None and process.process.is_alive:
            print("Join Process... " + process.name)
            process.process.join()
            process.parent.close()
            process.process = None
            process.parent = None
            process.isEnabled = False

    def terminateAll(self):
        self.isRunning = False
        for process in self.processes:
            self.terminateSubEngine(process)
        print("Done!")
