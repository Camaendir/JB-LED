from neopixel import *
from time import sleep

class StripArrangement:

    def __init__(self):
        self.isCreated = False
        self.layout = [] #StripObj,length,pin,dma,chanel
        self.pixellength = 0

    def addStrip(self, pPixellength, pPin, pDMA, pChanel, pIsReversed):
        if not self.isCreated:
            self.layout.append([pPixellength, pPin, pDMA, pChanel, pIsReversed])
            return True
        return False

    def setup(self):
        self.isCreated=True
        tmp=[]
        for row in self.layout:
            self.pixellength = self.pixellength + row[0]
            obj = Adafruit_NeoPixel(row[0], row[1], 1200000, row[2], False, 128, row[3])
            obj.begin()
            tmp.append([obj,row[0], row[4]])
        self.layout = tmp

    def setFrame(self, pFrame):
        for i in range(len(pFrame)):
            self.setPixel(i, pFrame[i])
        self.show()

    def setPixel(self, pPixel, color):
        count = 0
        for row in self.layout:
            if row[1] + count > pPixel:
                if row[2]:
                    row[0].setPixelColor(row[1]-(pPixel-count)-1, Color(color[1], color[0], color[2])) # inverted Strip not Implemented yet
                    break
                else:
                    row[0].setPixelColor(pPixel-count, Color(color[1], color[0], color[2]))
                    break
            else:
                count = count + row[1]


    def show(self):
        if self.isCreated:
            for row in self.layout:
                row[0].show()

    def test(self):
        for i in range(self.pixellength):
            self.setPixel(i, (255,0,0))
            self.show()
            sleep(0.5)
        for i in range(self.pixellength):
            self.setPixel(i, (0,0,0))
            self.show()