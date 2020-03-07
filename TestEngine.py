from Lib.Engine import Engine
from Lib.SubEngine import SubEngine
from Lib.Object import Object

class Test(SubEngine):

    def __init__(self, mqtt):
        self.build(mqtt,450,3)
        self.obj = Object()
        self.obj.build(True,0,[[255,255,255]]*450)
        self.addObj(self.obj,2)

    def update(self):
        if self.obj.content[0] == [0,0,0]:
            self.obj.content = [[255,255,255]]*450
        else:
            self.obj.content = [[0,0,0]]*450





if __name__ == '__main__':
    eng = Engine()
    eng.addSubEngine(Test('abc'), True)
    eng.run()
