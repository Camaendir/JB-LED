import time
import multiprocessing
import threading

import numpy as np

from BaseClasses.EngineProcess import EngineProcess
import paho.mqtt.client as mqtt

from BaseClasses.MqttAble import MqttAble
from BaseClasses.ResourceProcess import ResourceProcess


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
        self.resourceProcesses = {}
        self.threadLock = {}
        self.pipemanager = None
        self.framerate = 0.05

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
                EngineProcess(pSub, pSub.name if issubclass(pSub.__class__, MqttAble) else None, None, None, pIsEnabled,
                              pSub.isCompressed, pSub.compressor)
            )
        else:
            print('Could not add SubEngine, because Engine is already running')

    def pipeManager(self):
        rate = float(self.framerate) * 0.9
        while self.isRunning:
            for process in self.processes:
                if process.parent is None:
                    continue
                if process.parent.poll():
                    msg = process.parent.recv()
                    # if isinstance(msg, str):
                    #    pass
                    # else:
                    self.threadLock[process.name].acquire()
                    self.frames[process.name] = process.compressor.decompressFrame(
                        msg) if process.isCompressed else msg
                    self.threadLock[process.name].release()
                    #
            time.sleep(rate)

    def run(self):
        try:
            self.isRunning = True
            threading.Thread(target=self.pipeManager).start()
            self.controller.setup()
            self.pixellength = self.controller.pixellength
            self.startResources()
            while self.isRunning:
                fr = time.time()
                frames = [[-1, -1, -1]] * self.pixellength
                for process in self.processes:
                    if process.isEnabled and process.parent is not None and process.process is not None:
                        process.parent.send("f")
                for process in self.processes:
                    if process.isEnabled and process.parent is None and process.process is None:
                        self.startSubEngine(process)
                    elif not process.isEnabled and process.parent is not None and process.process is not None:
                        self.terminateSubEngine(process)
                    elif process.isEnabled:
                        self.threadLock[process.name].acquire()
                        frame = self.frames[process.name]
                        self.threadLock[process.name].release()
                        for i in range(len(frames)):
                            if frames[i] == [-1, -1, -1]:
                                frames[i] = frame[i]
                brPercent = float(self.brightness) / 100
                completeFrame = []
                for f in frames:
                    color = []
                    for a in f:
                        color.append(int(max(0, a) * brPercent))
                    completeFrame.append(color)
                self.controller.setFrame(completeFrame)
                fr = time.time() - fr
                if fr <= self.framerate:
                    time.sleep(self.framerate - fr)

        except KeyboardInterrupt:
            self.terminateAll()
        except Exception as error:
            print("Unexpected Error in Engine:", error)
            print("Terminating all SubEngines!")
            self.terminateAll()
            print("All SubEngines terminated.")
            print("Shutting down Engine.")

    def startResources(self):
        for key in self.resourceProcesses:
            if self.resourceProcesses[key].process is not None:
                self.resourceProcesses[key].process.start()

    def startSubEngine(self, engineProcess):
        if self.isRunning:
            if engineProcess.subengine.isRunning:
                print("Could not start SubEngine, because SubEngine is already running")
                return
            parent, child = multiprocessing.Pipe()
            process = multiprocessing.Process(target=engineProcess.subengine.run)
            resourcesToRegister = engineProcess.subengine.resourcesToRegister
            resourceNames = {}
            resourceLocks = {}
            for name in resourcesToRegister:
                resourceLocks[name] = self.resourceProcesses[name].lock
                resourceNames[name] = self.resourceProcesses[name].shmName
            engineProcess.subengine.configure(child, resourceNames, resourceLocks)
            engineProcess.process = process
            engineProcess.parent = parent
            engineProcess.isEnabled = True
            if engineProcess.name not in self.threadLock.keys():
                self.threadLock[engineProcess.name] = threading.Lock()
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
            print("Terminate Process... ")
            process.parent.send("t")
        if process.process is not None and process.process.is_alive:
            print("Join Process... ")
            process.process.join()
            process.parent.close()
            process.process = None
            process.parent = None
            process.isEnabled = False

    def terminateResourceProcess(self, process):
        if process.pipeParent is not None:
            process.pipeParent.send("t")
        if process.process is not None and process.process.is_alive:
            process.process.join()
            process.pipeParent.close()

    def terminateAll(self):
        self.isRunning = False
        for process in self.processes:
            self.terminateSubEngine(process)
        time.sleep(2)
        for key in self.resourceProcesses.keys():
            self.terminateResourceProcess(self.resourceProcesses[key])
        print("Done!")

    def registerResource(self, resource):
        if isinstance(resource.name, str):
            shm_name = resource.resource.shm.name
            lock = multiprocessing.Lock()
            parent, child = multiprocessing.Pipe()
            resource.configure(child, lock)
            process = multiprocessing.Process(target=resource.runEntry)
            self.resourceProcesses[resource.name] = ResourceProcess(shm_name, process, parent, lock)
        else:
            lock = {}
            parent, child = multiprocessing.Pipe()
            process = multiprocessing.Process(target=resource.runEntry)
            for i, nam in enumerate(resource.name):
                lck = multiprocessing.Lock()
                lock[nam] = lck
                self.resourceProcesses[nam] = ResourceProcess(resource.resource[nam].shm.name,
                                                              process if i == 0 else None, parent if i == 0 else None,
                                                              lck)
            resource.configure(child, lock)
