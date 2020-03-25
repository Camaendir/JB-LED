from Lib.Objects.Object import Object

class Background(Object):

    def __init__(self, pPixellength):
        self.color = [ 0, 0, 0]
        self.pixellength = pPixellength
        self.build(True, self.pixellength -1, [self.color] * self.pixellength)

    def setColor(self, color):
        self.content = [color] * self.pixellength