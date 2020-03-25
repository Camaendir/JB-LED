from Lib.SubEngine import *
from Lib.Objects.Object import *

from random import random

global pixellength
pixellength = 450 


class Background(Object):
    def __init__(self):
        self.color = [ 0, 0, 0]
        self.build(True, pixellength -1, [self.color] * pixellength)


    def setColor(self, color):
        self.content = [color] * pixellength

class Fading(SubEngine):

    def __init__(self):
        self.rgb = [255,0,0]
        self.phase = ([0, 1, 0], [-1, 0, 0], [0, 0, 1], [0, -1, 0], [1, 0, 0], [0, 0, -1])
        self.index = 0
        self.build("Fading",449, 5)

        self.p = Background()
        self.addObj(self.p)

    def onMessage(self, topic, payload):
        print(["Fading", topic, payload])

    def update(self):
        self.getColor()
        self.p.setColor(self.rgb)
    
    def getStates(self):
        return [["strip/info/Fading/enable",str(self.isEnabled)]]

    def getColor(self, speed=1):
        for i in range(3):
            self.rgb[i] = self.rgb[i] + (self.phase[self.index][i] * speed)
        
        if self.rgb[0] < 0 or self.rgb[0] > 255 or self.rgb[1] < 0 or self.rgb[1] > 255 or self.rgb[2] < 0 or self.rgb[2] > 255:
            for i in range(3):
                self.rgb[i] = self.rgb[i] - self.phase[self.index][i]

            self.index = self.index + 1

            if self.index >= len(self.phase):
                self.index = 0


class Lamp(SubEngine):

    def __init__(self):
        self.build("Lamp", pixellength ,1)
        self.rgb = [255, 135, 0]
        self.p = Background()
        self.addObj(self.p)
        self.isEnabled = False

    def update(self):
        if self.rgb != self.p.color:
            self.p.setColor(self.rgb)
        return

    def onMessage(self, topic, payload):
        if topic == "color":
            if payload.startswith("#"):
                self.rgb = [int(payload[1:3], 16), int(payload[3:5], 16), int(payload[5:7], 16)]
            elif payload.startswith("rgb("):
                payload = payload[4:len(payload) - 1].split(",")
                for i in range(3):
                    self.rgb[i] = int(payload[i])
        elif topic == "color/r":
            self.rgb[0] = int(payload)
        elif topic == "color/g":
            self.rgb[1] = int(payload)
        elif topic == "color/b":
            self.rgb[2] = int(payload)

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/Lamp/enable",str(self.isEnabled)])
        retVal.append(["strip/info/Lamp/color", '#%02x%02x%02x' % tuple(self.rgb)])
        return retVal

class Snake(Object):

    def __init__(self, length = 25, color = [255,0,0]):
        self.build(True,0,[])
        self.length = length
        self.setColor(color)
        self.double = self.position

    def move(self, speed = 1):
        self.double = self.double + speed 
        if self.double >= pixellength:
            self.double = 0
        elif self.double < 0:
            self.double = pixellength + self.double
        self.position = int(self.double)
    
    def setColor(self, color):
        self.rgb = color
        self.content = [color] * self.length

class Alarm(SubEngine):

    def __init__(self):
        self.build("Alarm", pixellength, 1)
        self.rgb = [255, 0, 0]
        self.obj = []

        for snk in range(9):
            self.obj.append(Snake(length = 15))
            self.obj[snk].double = snk * 50
            self.addObj(self.obj[snk])

    def setColor(self, color):
        for snk in range(9):
            self.obj[snk].setColor(color)

    def update(self):
        for snk in range(9):
            self.obj[snk].move()
            if self.obj[snk].rgb != self.rgb:
                self.obj[snk].setColor(self.rgb)

    def onMessage(self, topic, payload):
        if topic == "color":
            if payload.startswith("#"):
                self.rgb = [int(payload[1:3], 16), int(payload[3:5], 16), int(payload[5:7], 16)]
            elif payload.startswith("rgb("):
                payload = payload[4:len(payload) - 1].split(",")
                for i in range(3):
                    self.rgb[i] = int(payload[i])
        elif topic == "color/r":
            self.rgb[0] = int(payload)
        elif topic == "color/g":
            self.rgb[1] = int(payload)
        elif topic == "color/b":
            self.rgb[2] = int(payload)

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/Alarm/enable", str(self.isEnabled)])
        retVal.append(["strip/info/Alarm/color", '#%02x%02x%02x' % tuple(self.rgb)])
        return retVal


class MultiSnake(SubEngine):

    def __init__(self):
        self.snkCount = 10
        self.build("MultiSnake", pixellength, self.snkCount)
        self.snakes = [] 
        for i in range(self.snkCount):
            self.snakes.append([Snake(), 0.0, 0])
            self.respawn(self.snakes[i])
            self.addObj(self.snakes[i][0], layer=i)

    def onMessage(self, topic, payload):
        pass

    def update(self):
        for snk in self.snakes:
            snk[0].move(speed=snk[1])
            snk[2] = snk[2] - snk[1]
            if snk[2]<=0:
                self.respawn(snk)

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/MultiSnake/enable", str(self.isEnabled)])
        return retVal

    def respawn(self, wrapper):
        wrapper[0].length = rdm(3, 60)
        wrapper[0].setColor([rdm(0, 256), rdm(0, 256), rdm(0, 256)])
        wrapper[0].position = rdm(0, 450)
        wrapper[1] = rdm(1,10)*0.1+0.5
        wrapper[2] = rdm(200,800) 

def rdm(min, max):
    return int(min + (random() * (max-min)))

class TestEngine(SubEngine):

    def __init__(self):
        self.build("TestEngine", 450, 1)
        self.test = Panel()
        self.test.isVisible = True
        self.test.position = 370
        self.test.setContent([[255,0,0],[255,255,0],[0,0,255],[255,0,255]])
        self.test.stayMirrored(True)
        self.test.stayRepeated(True,15)
        self.test.stayLooped(True)
        self.addObj(self.test)
        self.isEnabled = False

    def update(self):
        self.test.shift(pixel=[255,255,255])
        pass

    def onMessage(self, topic, payload):
        pass

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/TestEngine/enable", str(self.isEnabled)])
        return retVal
