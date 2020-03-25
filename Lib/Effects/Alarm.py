from Lib.SubEngine import SubEngine
from Lib.Objects.Snake import Snake

class Alarm(SubEngine):

    def __init__(self, pPixellength):
        self.pixellength = pPixellength
        self.build("Alarm", self.pixellength, 1)
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