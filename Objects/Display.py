from socket import socket
from socket import AF_INET
from socket import SOCK_DGRAM

from threading import Thread


class Display:

    def __init__(self, pPort, pPixellength=10, pWhiteList=None):
        self.port = pPort
        self.pixellength = pPixellength
        self.whitelist = pWhiteList

        self.isVisible = True
        self.position = 0
        self.content = [[-1, -1, -1]] * self.pixellength

        self.isRunning = False
        self.thread = None
        self.sock = None

    def startSocket(self):
        if self.thread is None:
            self.sock = socket(AF_INET, SOCK_DGRAM)
            self.sock.bind(("127.0.0.1", self.port))
            self.thread = Thread(target=self.recive)
            self.thread.start()

    def terminateSocket(self):
        if self.thread is not None:
            self.isRunning = False
            Thread.join(self.thread)
            self.sock.close()

    def recive(self):
        self.isRunning = True
        while self.isRunning:
            try:
                data, addr = self.sock.recvfrom(self.pixellength * 3)
                if self.whitelist is not None:
                    pass
                else:
                    self.setContent(data)

            except:
                print("Display Object: Socket Error")

    def setContent(self, pBytes):
        frame = []
        block = []
        for byte in pBytes:
            if len(block) >= 3:
                frame.append(block)
                block = []
            block.append(int(byte))
        frame.append(block)
        if self.isContent(frame):
            self.content = frame

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
            print("Display Objekt: Wrong Input Format!")
            return False
        return True
