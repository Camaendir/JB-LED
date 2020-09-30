from colorsys import hls_to_rgb
import time
from BaseClasses.SubEngine import *

# Not implemented yet needs to wait for resource overhaul
class SpecTrain(SubEngine):

    def terminating(self):
        pass

    def __init__(self):
        raise NotImplementedError
        super().__init__("Train", 450, 1)
        self.adapter = Adapter()
        self.shift = 180
        self.adapter.daemon = True
        self.stated = False
        self.obj = Panel()
        self.obj.stayMirrored(True)
        self.obj.position = 245
        self.obj.setContent([[0, 0, 0]] * 225)
        self.addObj(self.obj)
        self.First = 0
        self.bufferlength = 11
        self.buffer = [[0, 0, 0]] * self.bufferlength
        self.gauss = (41, 26, 16, 7, 4, 1)
        self.buffermid = int((self.bufferlength - 1) / 2)
        self.gaussaverage = self.gauss[0]
        for i in range(self.buffermid):
            self.gaussaverage = self.gaussaverage + (2 * self.gauss[1 + i])

    def update(self):
        if not self.stated:
            self.adapter.start()
            time.sleep(7)
            self.stated = True
        data = self.adapter.fft_data[:]
        data = data[10:30]
        index = data.index(max(data))
        frame = [-1, 0]
        if data[index] >= 15:
            hue = index
            hue = float(hue) / len(data)
            frame = [hue, 1]
        self.buffer[0] = frame
        together = 0
        full_value = []
        for i in range(self.bufferlength):
            gaussindex = self.gauss[abs(i - self.buffermid)]
            if self.buffer[i][0] > -1:
                together = together + gaussindex
                full_value.append((self.buffer[i][0] * gaussindex, 0.5 * gaussindex))
            else:
                full_value.append((0, 0))
        fin = [0, 0]
        for elm in full_value:
            fin[0] = fin[0] + elm[0]
            fin[1] = fin[1] + elm[1]
        together = max(together, 1)
        fin[0] = float(fin[0]) / together
        fin[1] = float(fin[1]) / self.gaussaverage
        if fin[1] < 0.1:
            fin[1] = 0
        final = hls_to_rgb((fin[0] + self.shift) % 360, fin[1], 1)
        final = [int(i * 255) for i in final]
        self.obj.shift(final)
        for i in range(self.bufferlength - 1):
            self.buffer[self.bufferlength - 1 - i] = self.buffer[self.bufferlength - 2 - i]
