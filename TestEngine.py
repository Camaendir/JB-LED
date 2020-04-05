from Lib.Engine import Engine
from Lib.Effects.Alarm import Alarm
from Lib.Controller.FrameStreamer import FrameStreamer
from Lib.Controller.Console import Consol

if __name__ == '__main__':
    strip = Consol(30) #FrameStreamer("192.168.2.114", 6501, 450)
    eng = Engine()
    eng.setControler(strip)
    eng.addSubEngine(Alarm(30, 25), True)
    eng.run()
