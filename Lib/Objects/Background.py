from Lib.Objects.Object import Object

class Background(Object):

    def __init__(self, pPixellength):
        super().__init__(pContent=[[0,0,0]]*pPixellength)
        self.color = [ 0, 0, 0]
        self.pixellength = pPixellength

    def setColor(self, color):
        self.content = [color] * self.pixellength