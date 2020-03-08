from Lib.Engine import Engine
from Lib.SubEngine import SubEngine
from Lib.Panel import Panel

from MainLamp import *
from Musik import SpecTrain
from Puslar import Pulsar


class Test(SubEngine):

    def __init__(self, mqtt):
        self.build(mqtt,450,3)
        self.obj = Panel()
        self.obj.isMirrored = True
        self.setContent([[255,0,0]]*2+[[0,0,255]]*5)
        print(self.content)
        self.addObj(self.obj,2)

    def update(self):
        if self.obj.content[0] == [0,0,0]:
            self.obj.content = [[255,255,255]]*450
        else:
            self.obj.content = [[0,0,0]]*450





if __name__ == '__main__':
    eng = Engine()
    #eng.addSubEngine(Test('abc'), True)
    eng.addSubEngine(Alarm(), False)
    eng.addSubEngine(MultiSnake(), False)
    eng.addSubEngine(Pulsar(), True)
    #spec = SpecTrain()
    #spec.isCompressed = True 
    #eng.addSubEngine(spec, False)
    eng.run()
