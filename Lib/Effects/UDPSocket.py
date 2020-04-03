from Lib.SubEngine import SubEngine
from Lib.Objects.Object import Object

from threading import Thread
from time import sleep

from socket import socket
from socket import AF_INET
from socket import SOCK_DGRAM

class UDPSocket(SubEngine):

    def __init__(self, pPixellength, pPort):
        self.build("UDPSocket", pPixellength, 1)
        self.port = pPort
        self.display = Object()
        self.display.build(True, 0 ,[[-1,-1,-1]] * self.pixellength)
        self.addObj(self.display)
        self.isReciving = False
        self.thread = None
        self.sock = None

    def startSocket(self):
        if self.thread == None:
            self.thread = Thread(target=self.reciveData)
            self.thread.start()

    def reciveData(self):
        self.isReciving = True
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", self.port))
        while self.isReciving:
            try:
                data, addr = self.sock.recvfrom(self.pixellength*3)
            except:
                print("UDPSocket: Socket Error")
            self.setContent(data)

    def setContent(self, pBytes):
        frame = []
        block = []
        for byte in pBytes:
            if len(block)>=3:
                frame.append(block)
                block = []
            block.append(int(byte))
        frame.append(block)
        if self.isContent(frame):
            self.display.content = frame


    def isContent(self, pFrame):
        try:
            if len(pFrame) != self.pixellength:
                return False

            for pixel in pFrame:
                if len(pixel) != 3:
                    return False
                for color in pixel:
                    if type(color) is not int or color < 0 or color > 255:
                        return False
        except:
            print("UDPSocket: Wrong Input Format!")
            return False
        return True


    def terminateSocket(self):
        self.isReciving = False
        if self.thread != None:
            Thread.join(self.thread)

    def decompData(self, pFrame):
        block = []
        for data in pFrame:
            block.append(self.bitToRow(data))
        retVal = []
        for row in block:
            retVal = retVal + [row[1]]*(row[0]+1)
        return retVal

    def bitToRow(self, pBits):
        retVal = [0, [0, 0, 0]]
        retVal[0] = (pBits & 4278190080) >> 24
        if retVal[0] == 255:
            retVal[0] = pBits & 255
            retVal[1] = [-1,-1,-1]
        else:
            retVal[1][0] = (pBits & 16711680) >> 16
            retVal[1][1] = (pBits & 65280) >> 8
            retVal[1][2] = pBits & 255
        return retVal

    def update(self):
        if self.thread==None:
            self.startSocket()

    def onMessage(self, topic, payload):
        if topic == "TERMIANTE" and payload == "TERMINATE":
            if self.thread != None:
                self.terminateSocket()

    def getStates(self):
        return None