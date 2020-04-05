from Lib.Engine import Engine
from Lib.Effects.Alarm import Alarm
from Lib.Controller.FrameStreamer import FrameStreamer

if __name__ == '__main__':
    strip = FrameStreamer("192.168.2.114", 6501, 450)
    eng = Engine()
    eng.setControler(strip)
    eng.addSubEngine(Alarm(450,25), True)
    eng.run()
