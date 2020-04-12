from Lib.Controller.StripArrangement import StripArrangement
from Lib.Effects.FrameMaster import FrameMaster
from Lib.Engine import Engine
from Lib.SubEngine import SubEngine

from Lib.Objects.Object import Object

class TestEngine(SubEngine):

    def __init__(self):
        self.build("Test", 450, 1)
        self.obj = Object()
        self.obj.build(True,0,[])
        self.addObj(self.obj)

    def update(self):
        self.obj.content.append([255,0,255])
        pass


if __name__ == '__main__':
    strip = StripArrangement()
    strip.addStrip(205, 13, 11, 1, False)
    strip.addStrip(245, 18, 10, 0, True)

    eng = Engine()
    eng.setControler(strip)
    eng.startMQTT("strip")
    eng.addSubEngine(FrameMaster(450, "192.168.2.114", 6501), False)
    eng.addSubEngine(TestEngine(), True)
    eng.run()
