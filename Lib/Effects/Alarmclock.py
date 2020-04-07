from Lib.SubEngine import SubEngine
from time import localtime
from time import struct_time

class Alarmclock(SubEngine):

    def __init__(self, pPixellength):
        self.build("Alarmclock", pPixellength, 1)
        self.alarms = []

    def update(self):
        pass

    def onMessage(self, topic, payload):
        if topic == "setAlarm":
            self.alarms.append(struct_time)

    def getStates(self):
        return None