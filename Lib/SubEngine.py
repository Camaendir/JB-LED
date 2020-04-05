from Lib.Layer import Layer
from Lib.Compression import compFrame
from time import sleep

class SubEngine:

    def build(self, mqtttopic, pixellength, layercount):
        self.layList = []
        self.mqttTopic = mqtttopic
        self.isCompressed = True
        self.isRunning = False
        self.pixellength = pixellength
        self.transparent = [-1, -1, -1]

        for i in range(layercount):
            tmp = Layer()
            tmp.build(self.pixellength)
            self.layList.append(tmp)

    def configur(self, pPipe):
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
                self.controler()
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
            self.pipe.send(compFrame(plain))
        else:
            self.pipe.send(plain)

    def controler(self):
        buff = []
        while self.pipe.poll():
            buff.append(self.pipe.recv())
        if len(buff)==0:
            sleep(0.001)
        else:
            for stri in buff:
                if stri == "t":
                    self.isRunning = False
                    self.onMessage("TERMINATE","TERMINATE")
                elif stri == "f":
                    self.sendFrame()
                elif stri.startswith("m:"):
                    mqtt = stri[2:].split("/")
                    self.onMessage(mqtt[0], mqtt[1])