from Controller.Controller import Controller


class Console(Controller):

    def __init__(self, pPixellength):
        self.pixellength = pPixellength
        self.lastFrame = None

    def setup(self):
        print("Controller: Setup")

    def setFrame(self, pFrame):
        if self.lastFrame != pFrame:
            print("Current Frame: " + str(pFrame))
            self.lastFrame = pFrame
