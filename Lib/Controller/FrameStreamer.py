from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM

class FrameStreamer:

    def __init__(self, pAddress, pPort, pPixellength):
        self.addr = (pAddress, pPort)
        self.pixellength = pPixellength
        self.sock = None

    def setup(self):
        if self.sock == None:
            self.sock = socket(AF_INET, SOCK_STREAM)
            try:
                self.sock.connect(self.addr)
            except:
                print("FrameStreamer: Error")
                self.sock = None

    def setFrame(self, pFrame):
        if self.sock == None:
            self.setup()

        try:
            data = []
            for pixel in pFrame:
                for color in pixel:
                    data.append(color)
            self.sock.sendall(bytes(data))
            print("Frame Sended...")
        except:
            print("FrameStreamer: Error in setFrame")
            self.setup()