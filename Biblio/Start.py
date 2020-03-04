from Lib import *

class TestEffekt(SubEngine):

    def __init__(self):
        self.build("TestEffekt", 1)
        self.row = Row()
        self.row.isVisible=True
        self.row.setContent([[255,0,0]]*300)
        self.addObj(self.row)
        self.i = 0
        self.isEnabled = True

    def update(self):
        self.i = self.i+ 1

        if self.i >=300:
            self.i = 0

        if(self.row.kernelContent[self.i] == [255, 0, 0]):
            self.row.replace(self.i, [255, 255, 0])
        else:
            self.row.replace(self.i, [255, 0, 0])

    def getStates(self):
        pass

    def onMessage(self, t, p):
        print([t,p])

eng = Engine()
eff = TestEffekt()
eng.addSubEngine(eff)
print(eff.pixellength)
print(eff.index)
eng.run()
