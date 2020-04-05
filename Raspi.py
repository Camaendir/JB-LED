from Lib.Controller.StripArrangement import StripArrangement
from Lib.Effects.FrameMaster import FrameMaster
from Lib.Effects.Alarm import Alarm
from Lib.Engine import Engine


if __name__ == '__main__':
    strip = StripArrangement()
    strip.addStrip(245, 13, 11, 1, False)
    strip.addStrip(205, 18, 10, 0, True)

    eng = Engine()
    eng.setControler(strip)
    eng.startMQTT("strip")
    eng.addSubEngine(FrameMaster(450, "192.168.2.114", 6501), True)
    eng.addSubEngine(Alarm(450,15), False)
    eng.run()
