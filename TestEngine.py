from Lib.Engine import Engine
from Lib.Effects.Alarm import Alarm
from Lib.Effects.FrameMaster import FrameMaster

from Lib.SubEngine import SubEngine
from Lib.Objects.Display import Display

class TestEngine(SubEngine):

    def __init__(self):
        self.build("TestEngine", 16, 1)
        self.obj = Display(5001, 16)
        self.addObj(self.obj)

    def update(self):
        if self.obj.isRunning == False:
            self.obj.startSocket()

    def onMessage(self, topic, payload):
        pass

    def getStates(self):
        return None


if __name__ == '__main__':
    strip = None
    pycharm = True
    gui = False

    if not pycharm:
        from Lib.Controller.StripArrangement import StripArrangement
        strip = StripArrangement()
        strip.addStrip(16, 18, 10, 0, True)
    elif gui:
        import sys
        from Lib.Controller.TestControler import TestControler
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        strip = TestControler()
    else:
        from Lib.Controller.Console import Consol
        strip = Consol(450)

    eng = Engine()
    eng.setControler(strip)
    eng.addSubEngine(FrameMaster(450, 5001), True)
    eng.addSubEngine(Alarm(450, 15), False)
    eng.run()
