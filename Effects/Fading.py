from BaseClasses.MqttAble import MqttAble
from BaseClasses.SubEngine import SubEngine
from Objects.Background import Background


class Fading(SubEngine, MqttAble):

    def __init__(self, pPixellength):
        super().__init__("Fading", pPixellength, 1)
        self.rgb = [255, 0, 0]
        self.phase = ([0, 1, 0], [-1, 0, 0], [0, 0, 1], [0, -1, 0], [1, 0, 0], [0, 0, -1])
        self.index = 0
        self.p = Background(self.pixellength)
        self.addObj(self.p)

    def onMessage(self, topic, payload):
        print(["Fading", topic, payload])

    def update(self):
        self.getColor()
        self.p.setColor(self.rgb)

    def getStates(self):
        return [["strip/info/Fading/enable", str(self.isRunning)]]

    def getColor(self, speed=1):
        for i in range(3):
            self.rgb[i] = self.rgb[i] + (self.phase[self.index][i] * speed)

        if self.rgb[0] < 0 or self.rgb[0] > 255 or self.rgb[1] < 0 or self.rgb[1] > 255 or self.rgb[2] < 0 or self.rgb[
            2] > 255:
            for i in range(3):
                self.rgb[i] = self.rgb[i] - self.phase[self.index][i]

            self.index = self.index + 1

            if self.index >= len(self.phase):
                self.index = 0

    def terminating(self):
        pass
