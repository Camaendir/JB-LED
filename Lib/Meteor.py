from Lib.Object import Object
from colorsys import hls_to_rgb, rgb_to_hls
import random

class Meteor:

    def __init__(self): # double, int, [rgb]
        self.isUsed = False
        self.position = -1
        self.speed = 0
        self.size = 0
        self.basecolor = []
        self.pixel = []

        self.obj = Object()
        self.obj.build(False, 0, [])

    def getObject(self):
        return self.obj

    def spawn(self, pSpeed, pPosition, pSize, pBaseColor):
        self.isUsed = True
        self.speed = pSpeed
        self.obj.position = pPosition
        self.pixel = []
        self.flare = []
        for i in range(pSize):
            self.pixel.append([pBaseColor[:],0])
        self.size = pSize
        self.basecolor = pBaseColor


    def update(self):
        tailLeng = int(len(self.pixel)*0.75)
        tailMax = 5
        tailAvg = tailMax/tailLeng
        tailMask = []

        buffer = []
        for i in range(len(self.flare)):
            if self.flare[i][2] == [255, 255, 255]:
                buffer.append(i)
            else:
                self.flare[i][1] = self.flare[i][1] * 0.5
                self.flare[i][0] = int(self.flare[i][0] + self.flare[i][1])
                for j in range(3):
                    self.flare[i][2][j] = min(self.flare[i][2][j] + random.randint(10,35),255)

        for i in buffer:
            self.flare.pop(len(self.pixel)-i-1)

        for i in range(tailLeng):
            tailMask.append(int(i*tailAvg))

        offset = len(self.pixel)-tailLeng
        for i in range(tailLeng):
            self.pixel[i+offset][1] = self.pixel[i+offset][1] + tailMask[i]


        for i in range(len(self.pixel)):
            if random.randint(0,100) < self.pixel[i][1]:
                buffer.append(len(self.pixel)-i-1)

        for i in buffer:
            if self.speed<0:
                self.flare.append([i,-1*self.speed,self.pixel.pop(i)[0]])
            else:
                self.flare.append([i, self.speed, self.pixel.pop(i)[0]])

        content = []
        for i in range(len(self.pixel)):
            content.append(self.pixel[i][0])

        self.flare.sort()
        for f in self.flare:
            if f[0] > len(self.pixel):
                for i in range(f[0]-len(self.pixel)):
                    content.append([-1,-1,-1])
            content.insert(f[0], f[2])
        print(content)
        print(self.flare)





    def calcMasc(self, color, mask):
        return (color[0]+mask[0], color[1]+mask[1])


if __name__ == '__main__':
    m = Meteor()
    m.spawn(-5,0,20,[0,0,255])
    m.update()
    m.update()
