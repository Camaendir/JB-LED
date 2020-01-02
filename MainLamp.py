import math
from SubEngine import *


global pixellength
pixellength = 450 


class Panel(Object):
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

        self.p = Panel()
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
        self.p = Panel()
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
        self.build()
        self.length = length
        self.setColor(color)
        self.isVisible = True
        self.double = self.position

    def move(self, speed = 1):
        self.double = self.double + speed 
        if self.double >= pixellength:
            self.double = 0
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

