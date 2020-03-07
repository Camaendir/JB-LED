from neopixel import *

class Strip:

    def __init__(self):
        self.PIN_1 = 13
        self.PIN_2 = 18
        self.FREQ = 1200000
        self.DMA_1 = 11
        self.DMA_2 = 10
        self.BRIGHTNES = 128
        self.INVERT = False
        self.CHANNEL_1 = 1
        self.CHANNEL_2 = 0
        self.strip1 = None
        self.strip2 = None

    def create(self, pixel1 = 245, pixel2 = 205):
        self.strip1 = Adafruit_NeoPixel(pixel1, self.PIN_1, self.FREQ, self.DMA_1, self.INVERT, self.BRIGHTNES, self.CHANNEL_1)
        self.strip2 = Adafruit_NeoPixel(pixel2, self.PIN_2, self.FREQ, self.DMA_2, self.INVERT, self.BRIGHTNES, self.CHANNEL_2)
        self.strip1.begin()
        self.strip2.begin()

    def show(self):
        self.strip1.show()
        self.strip2.show()

    def setPixel(self, pixel, r=0, g=0, b=0, color=None):
        if color is None:
            if(pixel < 245):
                self.strip1.setPixelColor(pixel, Color(g,r,b))
            else:
                self.strip2.setPixelColor(205 - (pixel - 244), Color(g,r,b))
        else:
            if(pixel < 245):
                self.strip1.setPixelColor(pixel, Color(color[1],  color[0], color[2]))
            else:
                self.strip2.setPixelColor(205 - (pixel - 244), Color(color[1], color[0], color[2]))

    def fill(self, color):
        self.strip2.fill(color)
        self.strip1.fill(color)
        
    def test(self):
        for i in range(450):
            self.setPixel(i, 255,0,0)
            self.show()
        for i in range(450):
            self.setPixel(i, 0,0,0)
            self.show()

    def blackout(self):
        for i in range(450):
            self.setPixel(i, 0,0,0)
        self.show()


if __name__ == "__main__":
    a = Strip()
    a.create()
    a.test()
