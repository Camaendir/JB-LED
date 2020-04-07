from socket import *

from time import clock

class TCPServer:

    def __init__(self, pPort, pBufferSize, ip=None, hostname=None):
        self.sock = socket(AF_INET, SOCK_STREAM)
        try:
            if hostname == None:
                hostname = gethostname()
            if ip == None:
                ip = gethostbyname(hostname)
        except:
            print("Server: No Server Ip")

        self.host = [ip, hostname]

        self.addr = (self.host[0], pPort)
        self.sock.bind(self.addr)

        self.buffersize = pBufferSize
        self.timeout = 0
        self.streamTimeout = 0
        self.clockedOut = -1

        self.connection = [None, None]
        self.isConnected = False

    def setTimeout(self, pTimeout):
        self.timeout = pTimeout
        self.sock.settimeout(pTimeout)
        if self.isConnected:
            self.connection[0].settimeout(self.timeout)

    def setStreamTimeout(self, pTimeout):
        self.streamTimeout = pTimeout

    def listen(self):
        try:
            self.sock.listen(1)
            con, addr = self.sock.accept()
            if self.timeout > 0:
                con.settimeout(self.timeout)
            self.connection = [con, addr]
            self.isConnected = True
            return True
        except timeout:
            print("Server: Connection Timed out!")
        return False

    def reciveData(self):
        if self.isConnected:
            try:
                data = self.connection[0].recv(self.buffersize)
            except ConnectionResetError:
                self.disconnect()
                return
            if self.streamTimeout > 0:
                if len(data) == 0:
                    if self.clockedOut == -1:
                        self.clockedOut = clock()
                    elif clock() - self.clockedOut > self.streamTimeout:
                        self.disconnect()
                else:
                    if self.clockedOut != -1:
                        self.clockedOut = -1
            if len(data) == 0:
                return None
            return data

    def sendData(self, pData):
        data = bytes(pData)
        if self.isConnected and len(data) <= self.buffersize:
            self.sock.send(data)

    def disconnect(self):
        if self.isConnected:
            self.isConnected = False
            try:
                self.connection[0].shutdown(SHUT_RDWR)
            except:
                pass
            self.connection[0].close()
            self.connection = [None, None]
