import time
import multiprocessing
import threading

from BaseClasses.EngineProcess import EngineProcess
import paho.mqtt.client as mqtt
from BaseClasses.MqttAble import MqttAble
from BaseClasses.ResourceProcess import ResourceProcess


class Engine:

    def __init__(self):
        self.isRunning = False  # Global Shutdown
        self.processes = []     # All SubEngines
        self.frames = {}        # All current frames from the SubEngines
        self.controller = None  # Configured Controller
        self.pixellength = 0    # Global Pixellength
        self.resourceProcesses = {}  # All Resources
        self.threadLock = {}    # All Mutex for frame access
        self.framerate = 0.05   # Global Framerate

        # Waiting for MQTT-Overhaul
        self.mqtt_client = None  # MQTT-Client
        self.pretopic = None    # MQTT Topic Prefix

# ----------- MQTT -----------

    def startMQTT(self, pretopic, host="localhost", port=1883, timeout=60):
        self.pretopic = pretopic
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(host, port, timeout)
        self.mqtt_client.subscribe(pretopic + "/effect/#")
        self.mqtt_client.subscribe(pretopic + "/command")
        self.mqtt_client.subscribe(pretopic + "/color/#")
        self.mqtt_client.loop_start()

    def on_message(self, client, userdata, msg):
        if not self.isRunning:
            return
        topic = msg.topic
        if topic == self.pretopic + "/command":  # Command
            self.on_command(msg.payload, None)

        # elif topic.startswith(self.pretopic + "/color/"):  # Color change
            # sub_topic = topic[len(self.pretopic) + 7:]
            # if sub_topic == "brightness":
            #    self.brightness = int(msg.payload)

        elif topic.startswith(self.pretopic + "/effect/"):  # Effect Command
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

# ----------- Configuration -----------

    def setController(self, pController):
        self.controller = pController

    def addSubEngine(self, pSub, pIsEnabled):
        if not self.isRunning:
            self.processes.append(
                EngineProcess(pSub, pSub.name if issubclass(pSub.__class__, MqttAble) else None, None, None, pIsEnabled,
                              pSub.isCompressed, pSub.compressor)
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
        self.controller.setup()
        self.pixellength = self.controller.pixellength
        self.startResources()
        try:
            while self.isRunning:
                fr = time.time()
                frames = [[-1, -1, -1]] * self.pixellength
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
                        for i in range(len(frames)):
                            # if pixel is transparent -> Overwrite it
                            if frames[i] == [-1, -1, -1]:
                                frames[i] = frame[i]
                complete_frame = []
                for f in frames:
                    color = []
                    for a in f:
                        # Filter out negative and floating point values, ToDo: implement brightness
                        color.append(int(max(0, a)))
                    complete_frame.append(color)
                self.controller.setFrame(complete_frame)
                fr = time.time() - fr
                if fr <= self.framerate:
                    time.sleep(self.framerate - fr)
        except KeyboardInterrupt:
            self.terminateAll()
        except Exception as error:
            print("Unexpected Error in Engine:", error)
            self.terminateAll()
            print("Shutting down Engine.")

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
            self.frames[engineProcess.name] = ([[-1, -1, -1]] * self.pixellength)

    def terminateAll(self):
        self.isRunning = False
        for process in self.processes:
            process.terminate()
        for key in self.resourceProcesses.keys():
            self.resourceProcesses[key].terminate()
