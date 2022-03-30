from BaseClasses.MqttAble import MqttAble
from Objects.Snake import Snake


class Alarm(MqttAble):

    def __init__(self, pPixellength, pSnakelength, name="Alarm", mqtt_topic=None, snake_count=1):
        if mqtt_topic is None:
            mqtt_topic = name
        super().__init__(mqtt_topic, name, pPixellength)
        self.pixellength = pPixellength
        self.snakelength = pSnakelength
        self.rgb = [255, 0, 0]
        self.obj = []
        self.snake_count = snake_count

        for snk in range(self.snake_count):
            self.obj.append(Snake(self.pixellength, length=self.snakelength))
            self.obj[snk].double = snk * 50
            self.addObj(self.obj[snk])

    def setColor(self, color):
        for snk in range(self.snake_count):
            self.obj[snk].setColor(color)

    def update(self):
        for snk in range(self.snake_count):
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
        return [["strip/info/Alarm/enable", str(self.isRunning)],
                  ["strip/info/Alarm/color", '#%02x%02x%02x' % tuple(self.rgb)]]

    def terminating(self):
        pass
