from abc import ABC, abstractmethod
from BaseClasses.Layer import Layer
from BaseClasses.MqttAble import MqttAble
from Cogs.Compression.BlockCompression import BlockCompression
from time import sleep
from multiprocessing import shared_memory


class SubEngine(ABC):

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def terminating(self):
        pass

    def __init__(self, name, pixellength, layercount=1, compression=BlockCompression(), resourcesToRegister=()):
        self.layList = []
        self.name = name
        self.isCompressed = (compression is not None)
        self.isRunning = False
        self.pixellength = pixellength
        self.transparent = [-1, -1, -1]
        self.pipe = None
        self.compressor = compression
        self.resources = {}
        self.resourceLocks = None
        self.resourcesToRegister = resourcesToRegister

        for i in range(layercount):
            self.layList.append(Layer(self.pixellength))

    def configure(self, pPipe, resourceNames, resourceLocks):
        if not self.isRunning:
            self.pipe = pPipe
            for key in resourceNames.keys():
                self.resources[key] = shared_memory.ShareableList(name=resourceNames[key])
            self.resourceLocks = resourceLocks

    def addObj(self, obj, layer=0):
        self.layList[layer].addObj(obj)

    def delObj(self, obj):
        for layer in self.layList:
            layer.delObj(obj)

    def run(self):
        self.isRunning = True
        while self.isRunning:
            try:
                self.controller()
            except KeyboardInterrupt:
                self.isRunning = False
                self.terminating()
                self.cleanupResources()
            except Exception as error:
                print("SubEngine: Error in Controller")
                raise error

    def getResource(self, name):
        if name in self.resources.keys():
            self.resourceLocks[name].acquire()
            data = [a for a in self.resources[name]]
            self.resourceLocks[name].release()
            return data
        else:
            raise Exception("Resource named '" + name + "' was not registered by the Subengine")

    def sendFrame(self):
        self.update()
        plain = [self.transparent] * self.pixellength
        frames = []
        for i in range(len(self.layList)):
            frames.append(self.layList[i].getFrame())

        for i in range(len(frames)):
            for j in range(self.pixellength):
                if plain[j] == self.transparent:
                    plain[j] = frames[i][j]
        if self.isCompressed:
            self.pipe.send(self.compressor.compressFrame(plain))
        else:
            self.pipe.send(plain)

    def cleanupResources(self):
        for key in self.resources.keys():
            self.resources[key].shm.close()

    def controller(self):
        buff = []
        while self.pipe.poll():
            buff.append(self.pipe.recv())
        if len(buff) == 0:
            sleep(0.001)
        else:
            for stri in buff:
                if stri == "t":
                    self.isRunning = False
                    self.terminating()
                    self.cleanupResources()
                    print("SubEngine terminated")
                elif stri == "f":
                    self.sendFrame()
                elif stri.startswith("m:"):
                    if issubclass(self, MqttAble):
                        mqtt = stri[2:].split("/")
                        self.onMessage(mqtt[0], mqtt[1])