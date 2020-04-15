from Lib.Engine import Engine
from Lib.Effects.Lamp import Lamp
from Lib.Controller.FrameStreamer import FrameStreamer
from Lib.Controller.Console import Consol
from Lib.Connection.TCPServer import TCPServer
from time import sleep



if __name__ == '__main__':
    eng = Engine()
    eng.setControler(FrameStreamer("192.168.2.114", 6501, 450))
    eng.addSubEngine(Lamp(), True)
    eng.run()

