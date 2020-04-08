from BaseClasses.MqttAble import MqttAble
from BaseClasses.SubEngine import SubEngine
from time import struct_time


class Alarmclock(SubEngine, MqttAble):

    def __init__(self, pPixellength):
        super().__init__("Alarmclock", pPixellength, 1)
        self.alarms = []

    def update(self):
        pass

    def onMessage(self, topic, payload):
        if topic == "setAlarm":
            self.alarms.append(struct_time)

    def getStates(self):
        return None

    def terminating(self):
        pass
