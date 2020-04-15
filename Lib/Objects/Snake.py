from Lib.Objects.Object import Object

class Snake(Object):

    def __init__(self, pPixellength,length=25, color=[255, 0, 0]):
        super().__init__()
        self.pixellength = pPixellength
        self.length = length
        self.setColor(color)
        self.double = self.position

    def move(self, speed=1):
        self.double = self.double + speed
        if self.double >= self.pixellength:
            self.double = 0
        elif self.double < 0:
            self.double = self.pixellength + self.double
        self.position = int(self.double)

    def setColor(self, color):
        self.rgb = color
        self.content = [color] * self.length