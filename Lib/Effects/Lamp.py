from Lib.SubEngine import SubEngine
from Lib.Objects.Background import Background

class Lamp(SubEngine):

    def __init__(self, pColor = [255,135,0]):
        super().__init__("Lamp", 1)
        self.rgb = pColor
        self.p = None
        self.isEnabled = False

    def update(self):
        if self.p is None:
            self.p = Background(self.pixellength)
            self.addObj(self.p)
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