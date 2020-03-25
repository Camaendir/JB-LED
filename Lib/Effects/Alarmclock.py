from Lib.SubEngine import SubEngine

class Alarmclock(SubEngine):

    def __init__(self, pPixellength):
        self.build("Alarmclock", pPixellength, 1)

    def onMessage(self, topic, payload):
        pass

    def getStates(self):
        return None