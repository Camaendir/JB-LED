from Lib.Engine import Engine
from Lib.Effects.Alarm import Alarm
from Lib.Controler.StripArrangement import StripArrangement

if __name__ == '__main__':
    strip = StripArrangement()
    strip.addStrip(16, 18, 10, 0, True)
    eng = Engine()
    eng.setControler(strip)
    eng.addSubEngine(Alarm(16, 3), True)
    eng.run()
