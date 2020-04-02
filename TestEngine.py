from Lib.Engine import Engine
from Lib.Effects.Alarm import Alarm


if __name__ == '__main__':
    strip = None
    pycharm = True

    if not pycharm:
        from Lib.Controller.StripArrangement import StripArrangement
        strip = StripArrangement()
        strip.addStrip(16, 18, 10, 0, True)
    else:
        import sys
        from Lib.Controller.TestControler import TestControler
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        strip = TestControler()
    eng = Engine()
    eng.setControler(strip)
    eng.addSubEngine(Alarm(16, 3), True)
    eng.run()
