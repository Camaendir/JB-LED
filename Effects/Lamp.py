from BaseClasses.MqttAble import MqttAble
from BaseClasses.SubEngine import SubEngine
from Objects.Background import Background


class Lamp(SubEngine, MqttAble):

    def __init__(self, pPixellength):
        super().__init__("Lamp", pPixellength, 1)
        self.pixellength = pPixellength
        self.rgb = [255, 135, 0]
        self.p = Background(self.pixellength)
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
        return [["strip/info/Lamp/enable", str(self.isEnabled)],
                  ["strip/info/Lamp/color", '#%02x%02x%02x' % tuple(self.rgb)]]

    def terminating(self):
        pass
