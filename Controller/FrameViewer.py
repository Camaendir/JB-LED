from threading import Thread
import pygame
from Controller.Controller import Controller


class FrameViewer(Controller):

    def __init__(self, pPixellength, pPixelSize=20):
        super().__init__()
        self.pixellength = pPixellength
        self.pixelsize = pPixelSize
        self.pixel = []
        self.frame = None
        self.display = None

    def setup(self):
        self.run()

    def setFrame(self, pFrame):
        if len(pFrame) == self.pixellength:
            for i in range(self.pixellength):
                pygame.draw.rect(self.display, pFrame[i], (self.pixelsize*i, 0, self.pixelsize, self.pixelsize))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise Exception("Closed Window")

    def run(self):
        pygame.init()
        self.display = pygame.display.set_mode((self.pixellength * self.pixelsize, self.pixelsize))
        self.display.fill((0, 0, 0))
