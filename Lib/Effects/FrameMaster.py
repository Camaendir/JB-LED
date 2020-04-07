from Lib.SubEngine import SubEngine
from Lib.Objects.Object import Object
from Lib.Connection.TCPServer import TCPServer
from Lib.Compression import decompFrame

from threading import Thread



class FrameMaster(SubEngine):

    def __init__(self, pPixellength, pIp, pPort):
        self.build("FrameMaster", pPixellength, 1)
        self.ip = pIp
        self.port = pPort

        self.display = Object()
        self.display.build(True, 0 ,[[-1,-1,-1]] * self.pixellength)
        self.addObj(self.display)

        self.isReciving = False
        self.thread = None
        self.tcpServer = None

    def startServer(self):
        if self.thread == None:
            self.thread = Thread(target=self.runSever)
            self.thread.start()

    def closeServer(self):
        if self.thread != None:
            self.isReciving = False
            self.tcpServer.disconnect()

    def runSever(self):
        self.tcpServer = TCPServer(self.port, self.pixellength*3, ip=self.ip)
        self.tcpServer.setStreamTimeout(0.5)
        self.isReciving = True
        while self.isReciving:
            if self.tcpServer.isConnected:
                data = self.tcpServer.reciveData()
                if data != None:
                    self.setContent(data)
            else:
                print("Listen")
                self.tcpServer.listen()

    def setContent(self, pBytes):
        buffer = []
        frame = []
        for byte in pBytes:
            if len(buffer) < 3:
                buffer.append(int(byte))
            else:
                frame.append(buffer)
                buffer = [byte]
        frame.append(buffer)
        self.display.content = frame

    def update(self):
        if self.thread == None:
            self.startServer()

    def onMessage(self, topic, payload):
        if topic == "TERMINATE" and payload == "TERMINATE":
            self.closeServer()

    def getStates(self):
        return None