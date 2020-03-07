from Layer import Layer

class SubEngine:

    def build(self, mqtttopic, pixellength, layercount):
        self.layList = []
        self.mqttTopic = mqtttopic
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
            self.update()
            plain = [self.transparent] * self.pixellength
            frames = []
            for i in range(len(self.layList)):
                frames.append(self.layList[i].getFrame())

            for i in range(len(frames)):
                for j in range(self.pixellength):
                    if plain[j] == self.transparent and frames[i][j] != self.transparent:
                        plain[j] = frames[i][j]
            self.pipe.send(plain)
            self.controler()

    def controler(self):
        buff = []
        buff.append(self.pipe.recv())
        while self.pipe.poll():
            buff.append(self.pipe.recv())
        keepgoing = False
        for stri in buff:
            if stri == "t":
                self.isRunning = False
            elif stri.startswith("m:"):
                mqtt = stri[2:].split("/")
            elif stri == "f":
                keepgoing = True
        if not keepgoing and self.isRunning:
            self.controler()

