from Objects.Object import Object


class Background(Object):

    def __init__(self, pPixellength):
        super().__init__(True, self.pixellength - 1, [self.color] * self.pixellength)
        self.color = [0, 0, 0]
        self.pixellength = pPixellength

    def setColor(self, color):
        self.content = [color] * self.pixellength
