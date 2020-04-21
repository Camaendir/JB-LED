from abc import ABC, abstractmethod
from BaseClasses.Layer import Layer
from BaseClasses.MqttAble import MqttAble
from Cogs.Compression.BlockCompression import BlockCompression
from time import sleep


class SubEngine(ABC):

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def terminating(self):
        pass

    def __init__(self, name, pixellength, layercount=1, compression=BlockCompression()):
        self.layList = []
        self.name = name
        self.isCompressed = True
        self.isRunning = False
        self.pixellength = pixellength
        self.transparent = [-1, -1, -1]
        self.pipe = None
        self.compressor = compression

        for i in range(layercount):
            self.layList.append(Layer(self.pixellength))

    def configure(self, pPipe):
        if not self.isRunning:
            self.pipe = pPipe

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
            except Exception as error:
                print("SubEngine: Error in Controler")
                print(str(error))

    def sendFrame(self):
        self.update()
        plain = [self.transparent] * self.pixellength
        frames = []
        for i in range(len(self.layList)):
            frames.append(self.layList[i].getFrame())

        for i in range(len(frames)):
            for j in range(self.pixellength):
                if plain[j] == self.transparent and frames[i][j] != self.transparent:
                    plain[j] = frames[i][j]
        if self.isCompressed:
            self.pipe.send(self.compressor.compressFrame(plain))
        else:
            self.pipe.send(plain)

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
                elif stri == "f":
                    self.sendFrame()
                elif stri.startswith("m:"):
                    if issubclass(self, MqttAble):
                        mqtt = stri[2:].split("/")
                        self.onMessage(mqtt[0], mqtt[1])
