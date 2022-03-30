import time
import multiprocessing
import threading
import traceback
from typing import List

from BaseClasses.EngineProcess import EngineProcess
import paho.mqtt.client as mqtt
from BaseClasses.MqttAble import MqttAble
from BaseClasses.ResourceProcess import ResourceProcess


class Engine:

    def __init__(self, enable_mqtt=False):
        self.isRunning = False  # Global Shutdown
        self.processes: List[EngineProcess] = []     # All SubEngines
        self.frames = {}        # All current frames from the SubEngines
        self.controller = []  # Configured Controller
        self.pixelLength = 0    # Global Pixellength
        self.resourceProcesses = {}  # All Resources
        self.threadLock = {}    # All Mutex for frame access
        self.framerate = 0.05   # Global Framerate

        # Waiting for MQTT-Overhaul
        self.mqtt_client = None  # MQTT-Client
        self.pretopic = None    # MQTT Topic Prefix

        if enable_mqtt:
            self.startMQTT("/led")

# ----------- MQTT -----------

    def startMQTT(self, pretopic, host="192.168.178.69", port=1883, timeout=60):
        self.pretopic = pretopic
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(host, port, timeout)
        self.mqtt_client.subscribe(pretopic + "/effect/#")
        self.mqtt_client.subscribe(pretopic + "/command")
        self.mqtt_client.loop_start()

    def on_message(self, client, userdata, msg):
        if not self.isRunning:
            return
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        if topic == self.pretopic + "/command":  # Command
            self.on_command(payload, None)

        elif topic.startswith(self.pretopic + "/effect/"):  # Effect Command
            sub_topic = topic[len(self.pretopic) + 8:]
            for process in self.processes:
                if process.isMqtt:
                    if sub_topic.startswith(process.mqttTopic + "/"):
                        effect_topic = sub_topic[len(process.mqttTopic) + 1:]
                        if effect_topic == "enable":
                            enabled = payload.lower() in ("true", "t", "1", "on")
                            if enabled:
                                self.startSubEngine(process)
                            else:
                                process.terminate()
                            process.isEnabled = enabled
                        elif process.parent is not None:
                            process.parent.send("m:" + effect_topic + "#" + payload)

    def on_command(self, command, attributes):
        if command == "reset":
            self.resetFrame()
        elif command == "shutdown":
            for process in self.processes:
                process.terminate()
                process.isEnabled = False

# ----------- Configuration -----------

    def registerController(self, pController, start_pixel, end_pixel):
        if self.isRunning:
            return
        self.controller.append((pController, start_pixel, end_pixel))

    def addSubEngine(self, pSub, pIsEnabled, startPixel):
        if not self.isRunning:
            self.processes.append(
                EngineProcess(pSub, pSub.name, None, None, pIsEnabled,
                              pSub.isCompressed, pSub.compressor, startPixel, pSub.mqttTopic if issubclass(pSub.__class__, MqttAble) else None)
            )
        else:
            print('Could not add SubEngine, because Engine is already running')

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

# ----------- Main Loop Functions -----------

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
        self.isRunning = True
        threading.Thread(target=self.pipeManager).start()
        self.pixelLength = 0
        for controller, _, end_pixel in self.controller:
            controller.setup()
            self.pixelLength = max(self.pixelLength, end_pixel)
        self.startResources()
        try:
            while self.isRunning:
                fr = time.time()
                frames = [[-1, -1, -1]] * self.pixelLength
                for process in self.processes:
                    # Send Frame request to every enabled SubEngine
                    if process.isEnabled and process.parent is not None and process.process is not None:
                        process.parent.send("f")
                for process in self.processes:
                    # Start SubEngine if not started
                    if process.isEnabled and process.parent is None and process.process is None:
                        self.startSubEngine(process)
                    # Terminate SubEngine if not terminated
                    elif not process.isEnabled and process.parent is not None and process.process is not None:
                        process.terminate()
                    # Get Frame from the SubEngine
                    elif process.isEnabled:
                        self.threadLock[process.name].acquire()
                        frame = self.frames[process.name]
                        self.threadLock[process.name].release()
                        for i in range(len(frame)):
                            if (i + process.startPixel) > len(frames) - 1:
                                break
                            # if pixel is transparent -> Overwrite it
                            if frames[process.startPixel + i] == [-1, -1, -1]:
                                frames[process.startPixel + i] = frame[i]
                complete_frame = []
                for f in frames:
                    color = []
                    for a in f:
                        # Filter out negative and floating point values
                        color.append(int(max(0, a)))
                    complete_frame.append(color)
                self.setFrame(complete_frame)
                fr = time.time() - fr
                if fr <= self.framerate:
                    time.sleep(self.framerate - fr)
        except KeyboardInterrupt:
            self.terminateAll()
        except Exception as error:
            print(traceback.format_exc())
            print("Unexpected Error in Engine:", error)
            self.terminateAll()
            print("Shutting down Engine.")

    def setFrame(self, frame):
        for controller, start, end in self.controller:
            controller.setFrame(frame[start:end])

    def resetFrame(self):
        for controller, start, end in self.controller:
            controller.setFrame([[0,0,0]] * (end - start))

# ----------- Start and terminate SubProcesses -----------

    def startResources(self):
        for key in self.resourceProcesses:
            if self.resourceProcesses[key].process is not None:
                self.resourceProcesses[key].process.start()

    def startSubEngine(self, engineProcess):
        if self.isRunning:
            if engineProcess.subengine.isRunning:
                return
            parent, child = multiprocessing.Pipe()
            process = multiprocessing.Process(target=engineProcess.subengine.run)
            resources_to_register = engineProcess.subengine.resourcesToRegister
            resource_names = {}
            resource_locks = {}
            for name in resources_to_register:
                resource_locks[name] = self.resourceProcesses[name].lock
                resource_names[name] = self.resourceProcesses[name].shmName
            engineProcess.subengine.configure(child, resource_names, resource_locks)
            engineProcess.process = process
            engineProcess.parent = parent
            engineProcess.isEnabled = True
            if engineProcess.name not in self.threadLock.keys():
                self.threadLock[engineProcess.name] = threading.Lock()
            process.start()
            self.frames[engineProcess.name] = ([[-1, -1, -1]] * (self.pixelLength - engineProcess.startPixel))

    def terminateAll(self):
        self.isRunning = False
        for process in self.processes:
            process.terminate()
        for key in self.resourceProcesses.keys():
            self.resourceProcesses[key].terminate()
