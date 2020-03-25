from Lib.Engine import Engine
from Lib.Objects.Panel import Panel

from MainLamp import *
from Musik import SpecTrain

class Test(SubEngine):

    def __init__(self, mqtt):
        self.build(mqtt,450,3)
        self.obj = Panel()
        self.obj.isVisible = True
        self.obj.position = 358
        self.obj.stayMirrored(True)
        self.obj.setContent([[255,0,0]]*2+[[0,0,255]]*5)
        print(self.obj.content)
        self.addObj(self.obj,2)

    def update(self):
        pass




if __name__ == '__main__':
    eng = Engine()
    #eng.addSubEngine(Test('abc'), True)
    eng.addSubEngine(Alarm(), False)
    eng.addSubEngine(MultiSnake(), False)
    spec = SpecTrain() 
    eng.addSubEngine(spec, True)
    eng.run()
