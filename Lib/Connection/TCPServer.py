from socket import *
from threading import Thread

from time import clock

class TCPServer:

    def __init__(self, pPort, pBufferSize, ip=None, hostname=None):
        try:
            if hostname == None:
                hostname = gethostname()
            if ip == None:
                ip = gethostbyname(hostname)
        except:
            print("Server: No Server Ip")

        self.host = [ip, hostname]
        self.addr = (self.host[0], pPort)
        print(self.addr)
        self.sock = socket(AF_INET, SOCK_STREAM)

        self.sock.bind(self.addr)
        self.whitelist = []


        self.buffersize = pBufferSize
        self.buffer = []

        self.timeout = 60
        self.sock.settimeout(self.timeout)
        self.streamTimeout = 0
        self.clockedOut = -1

        self.connection = [None, None]
        self.isConnected = False

        self.isRunning = False
        self.thread = None

    def setTimeout(self, pTimeout):
        self.timeout = pTimeout
        self.sock.settimeout(pTimeout)
        if self.isConnected:
            self.connection[0].settimeout(self.timeout)

    def setStreamTimeout(self, pTimeout):
        self.streamTimeout = pTimeout

    def addWhitlistedIp(self, pIp):
        if not self.isRunning:
            self.whitelist.append(pIp)

    def startServer(self):
        if not self.isRunning and self.thread is None:
            self.thread = Thread(target=self.run)
            self.isRunning = True
            self.thread.start()

    def run(self):
        self.isRunning = True
        while self.isRunning:
            if self.isConnected:
                data = self.reciveData()
                if data is not None:
                    self.buffer.append(data)
            else:
                self.listen()

    def listen(self):
        print("Server: Listen " + str(self.addr))
        try:
            self.sock.listen(1)
            con, addr = self.sock.accept()
            if len(self.whitelist) > 0:
                accepted = False
                for ip in self.whitelist:
                    if ip == addr[0]:
                        accepted = True
                if not accepted:
                    return False

            if self.timeout > 0:
                con.settimeout(self.timeout)
            self.connection = [con, addr]
            self.isConnected = True
            print("Server: Connected! "+ str(self.connection[1]))
            return True
        except timeout:
            print("Server: Nothing Conected!(TIMEOUT)")
        return False

    def reciveData(self):
        if self.isConnected:
            try:
                data = self.connection[0].recv(self.buffersize)
            except ConnectionResetError:
                self.disconnect()
                return
            except Exception as e:
                print(str(e))
                return
            if self.streamTimeout > 0:
                if len(data) == 0:
                    if self.clockedOut == -1:
                        self.clockedOut = clock()
                    elif clock() - self.clockedOut > self.streamTimeout:
                        print("Server: Stream Error (TIMEOUT)")
                        self.disconnect()
                else:
                    if self.clockedOut != -1:
                        self.clockedOut = -1
            if len(data) == 0:
                return None
            return data
        return None

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
            print("Server: Disconected! "+ str(self.connection[1]))
            self.connection = [None, None]

    def stopServer(self):
        self.disconnect()
        if self.thread is not None:
            self.isRunning = False
            self.thread
            self.thread = None
