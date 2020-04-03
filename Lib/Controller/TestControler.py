import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon



class TestControler(QWidget):

    def __init__(self, pPixellength = 16):
        print("Controler:__init__")
        self.pixellength = pPixellength

        super().__init__()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()


    def setup(self):
        print("Controler:SetUp")

    def setFrame(self, pFrame):
        print("Controler:setFrame")
        print(pFrame)
