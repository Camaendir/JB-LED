from Lib.Connection.TCPClient import TCPClient
from Lib.Compression import compFrame

class FrameStreamer:

    def __init__(self, pAddress, pPort, pPixellength):
        self.tcp = TCPClient(pAddress, pPort, pPixellength*3)
        self.tcp.setTimeout(1)
        self.pixellength = pPixellength

    def setup(self):
        self.tcp.connect()

    def setFrame(self, pFrame):
        if self.tcp.isConnected:
            self.tcp.sendData(compFrame(pFrame))