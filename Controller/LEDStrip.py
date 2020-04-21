from Controller import Controller
from Controller.neopixel import *
from time import sleep


class LEDStrip(Controller):

    def __init__(self):
        self.isCreated = False
        self.layout = []  # StripObj,length,pin,dma,chanel
        self.pixellength = 0
        self.prelayout = []

    def addStrip(self, pPixellength, pPin, pDMA, pChanel, pIsReversed):
        if self.isCreated:
            return False
        self.prelayout.append([pPixellength, pPin, pDMA, pChanel, pIsReversed])
        return True

    def setup(self):
        self.isCreated = True
        for row in self.prelayout:
            self.pixellength = self.pixellength + row[0]
            obj = Adafruit_NeoPixel(row[0], row[1], 1200000, row[2], False, 128, row[3])
            obj.begin()
            self.layout.append([obj, row[0], row[4]])

    def setFrame(self, pFrame):
        for i in range(len(pFrame)):
            self.setPixel(i, pFrame[i])
        self.show()

    def setPixel(self, pPixel, color):
        if not self.isCreated:
            return
        for row in self.layout:
            if row[1] > pPixel:
                row[0].setPixelColor((row[1] - pPixel - 1 if row[2] else pPixel), Color(color[1], color[0], color[2]))
                break
            else:
                pPixel = pPixel - row[1]

    def show(self):
        if not self.isCreated:
            return
        for row in self.layout:
            row[0].show()

    def test(self):
        for i in range(self.pixellength):
            self.setPixel(i, (255, 0, 0))
            self.show()
            sleep(0.5)
        for i in range(self.pixellength):
            self.setPixel(i, (0, 0, 0))
            self.show()
