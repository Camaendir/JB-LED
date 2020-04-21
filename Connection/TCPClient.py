from socket import *
import time


class TCPClient:

    def __init__(self, pAddr, pPort, pBuffersize):
        self.addr = (pAddr, pPort)
        self.buffersize = pBuffersize
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.isConnected = False

    def setTimeout(self, pTimeout):
        self.sock.settimeout(pTimeout)

    def connect(self):
        try:
            self.sock.connect(self.addr)
            self.isConnected = True
        except timeout:
            print("Client: Timed out")

    def sendData(self, pData):
        data = bytes(pData)
        if self.isConnected and len(data) <= self.buffersize:
            try:
                self.sock.send(data)
            except ConnectionResetError:
                self.disconnect()

    def receiveData(self):
        if self.isConnected:
            try:
                return self.sock.recv(self.buffersize)
            except ConnectionResetError:
                self.disconnect()

    def disconnect(self):
        if self.isConnected:
            self.sock.shutdown(SHUT_RDWR)
            self.sock.close()
            self.isConnected = False
