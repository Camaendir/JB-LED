from SubEngine import *

global pixellength
pixellength = 450


class Panel(Object):
    def __init__(self):
        self.color = [ 0, 0, 0]
        self.build(True, pixellength, [self.color] * pixellength)


    def setColor(self, color):
        self.content = [color] * pixellength
        print(self.content)


class Fading(SubEngine):

    def __init__(self):
        self.rgb = [255,0,0]
        self.phase = ([0, 1, 0], [-1, 0, 0], [0, 0, 1], [0, -1, 0], [1, 0, 0], [0, 0, -1])
        self.index = 0
        self.build("Fading",pixellength, 5)

        self.p = Panel()
        self.addObj(self.p)


    def onMessage(self, topic, payload):
        print([topic, payload])


    def update(self):
        self.getColor()
        self.p.setColor(self.rgb)
        print(self.rgb)

    def getColor(self, speed=1):
        for i in range(3):
            self.rgb[i] = self.rgb[i] + (self.phase[self.index][i] * speed)
        
        if self.rgb[0] < 0 or self.rgb[0] > 255 or self.rgb[1] < 0 or self.rgb[1] > 255 or self.rgb[2] < 0 or self.rgb[2] > 255:
            for i in range(3):
                self.rgb[i] = self.rgb[i] - self.phase[self.index][i]

            self.index = self.index + 1

            if self.index >= len(self.phase):
                self.index = 0
