from Objects.Object import Object


class Background(Object):

    def __init__(self, pPixellength):
        self.pixellength = pPixellength
        self.color = [0, 0, 0]
        super().__init__(True, self.pixellength - 1, [self.color] * self.pixellength)

    def setColor(self, color):
        self.color = color
        self.content = [color] * self.pixellength
