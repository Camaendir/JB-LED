
class Consol:

    def __init__(self, pPixellength):
        self.pixellength = pPixellength
        self.lastFrame = None

    def setup(self):
        print("Controler: Setup")

    def setFrame(self, pFrame):
        if self.lastFrame != pFrame:
            print("Current Frame: " + str(pFrame))
            self.lastFrame = pFrame