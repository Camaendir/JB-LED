from Controller.Controller import Controller


class Console(Controller):

    def __init__(self, pPixellength, name="Console"):
        self.pixellength = pPixellength
        self.lastFrame = None
        self.name = name

    def setup(self):
        print("Controller: Setup")

    def setFrame(self, pFrame):
        if self.lastFrame != pFrame:
            image = str(pFrame).replace(" ", "")
            print(f"{self.name}: {image}")
            self.lastFrame = pFrame
