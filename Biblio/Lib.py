import multiprocessing
import time

class Engine:

    def __init__(self):
        self.isRunning = False
        self.brightnis = 100
        self.subengines = []
        self.processes =[]

    def addSubEngine(self, pSub, pIsEnabled):
        if not self.isRunning:
            self.subengines.append(pSub)
            self.processes.append([pSub.mqttTopic, None, None, pIsEnabled])

    def run(self):
        self.isRunning = True

        while self.isRunning:
            for row in self.processes:
                if row[3] and row[2]==None and row[1] == None:
                    self.startSubEngine(row[0])
                elif not row[3] and row[2] != None and row[1] != None:
                    #self.terminateSubEngine(row[0])
                    pass
                else:
                    print(row[2].recv())
                    row[2].send("")
            time.sleep(1)
        self.terminate()

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

    def terminateSubEngine(self, pMqttTopic):
        for row in self.processes:
            if row[0] == pMqttTopic:
                print("Terminate: "+pMqttTopic)
                row[2].send("t")
                print("Joining Process...")
                row[1].join()
                print("Done!")
                row[2].unlink()
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
            row[2].unlink()
            row[1] = None
            row[2] = None
        print("Done!")

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

    def addObj(self, obj,layer=0):
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
        str = self.pipe.recv()
        if str =="t":
            self.isRunning = False
        elif str.startswith("m:"):
            mqtt = str[2:].split("/")


class Layer:

    def build(self, pixellength):
        self.objList = []
        self.pixellength = pixellength
        self.transparent = [-1, -1, -1]

    def addObj(self, obj):
        self.objList.append(obj)

    def delObj(self, obj):
        self.objList.remove(obj)

    def getFrame(self):
        field = []
        for i in range(self.pixellength):
            field.append(self.transparent)

        for obj in self.objList:
            if obj.isVisible:
                for i in range(len(obj.content)):
                    index = obj.position - i
                    if index < 0:
                        index = self.pixellength + index
                    field[index] = obj.content[i]
        return field


class Object:

    def build(self, isVisible, position, content):
        self.isVisible = isVisible
        self.position = position
        self.content = content


class Test(SubEngine):

    def __init__(self):
        self.build("Test",450,3)
        self.obj = Object()
        self.obj.build(True,0,[[255,255,255]]*450)
        self.addObj(self.obj,2)

    def update(self):
        if self.obj.content[0]==[0,0,0]:
            self.obj.content = [[255,255,255]]*450
        else:
            self.obj.content = [[0,0,0]]*450


def compFrame(pFrame):
    block = []
    currentBlock = 0
    lastPixel = pFrame.pop(0)
    for pixel in pFrame:
        if lastPixel == pixel:
            if currentBlock >= 254:
                block.append([lastPixel, currentBlock])
                currentBlock = 0
            else:
                currentBlock = currentBlock + 1
        else:
            block.append([lastPixel,currentBlock])
            currentBlock = 0
            lastPixel = pixel
    block.append([lastPixel,currentBlock])
    retVal = []
    for b in block:
        retVal = rowToBits(b)
    return retVal

def rowToBits(pRow):
    if pRow[1] == [-1, -1, -1]:
        retVal = (255 << 24) + pRow[0]
    else:
        retVal = (pRow[0] << 24) + (pRow[1][0] << 16) + (pRow[1][1] << 8) +pRow[1][2]
    return retVal

def bitToRow(pBits):
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





if __name__ == '__main__':
    if not True:
        eng = Engine()
        t = Test()
        for _ in range(10):
            eng.addSubEngine(t, True)
            eng.startSubEngine("Test")
        eng.run()

    elif  True:
        testFrame = [[255,255,255]]*20+[[0,0,0]]*16+[[-1, -1, -1]]*12000
        print(testFrame)
        print(compFrame(testFrame))




