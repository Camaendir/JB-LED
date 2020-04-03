from socket import socket
from socket import AF_INET
from socket import SOCK_DGRAM

class FrameStreamer:

    def __init__(self, pAddress, pPort, pPixellength):
        self.addr = (pAddress, pPort)
        self.pixellength = pPixellength
        self.sock = None

    def setup(self):
        if self.sock == None:
            self.sock = socket(AF_INET, SOCK_DGRAM)

    def setFrame(self, pFrame):
        try:
            data = []
            for pixel in pFrame:
                for color in pixel:
                    data.append(color)
            self.sock.sendto(bytes(data), self.addr)
        except:
            print("FrameStreamer: Error in setFrame")