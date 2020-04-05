from Lib.Engine import Engine
from Lib.Effects.Alarm import Alarm
from Lib.Effects.FrameMaster import FrameMaster
from Lib.Controller.Console import Consol

if __name__ == '__main__':
    strip = Consol(5)  # FrameStreamer("192.168.2.114", 6501, 450) #
    eng = Engine()
    eng.setControler(strip)
    eng.addSubEngine(FrameMaster(5, "192.168.2.109", 6501), True)
    eng.addSubEngine(Alarm(5, 1), False)
    eng.run()
