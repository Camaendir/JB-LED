class TestControler:

    def __init__(self):
        print("Controler:__init__")
        self.pixellength = 16

    def setup(self):
        print("Controler:SetUp")

    def setFrame(self, pFrame):
        print("Controler:setFrame")
        print(pFrame)