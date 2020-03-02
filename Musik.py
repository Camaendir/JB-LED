#Basierend auf https://www.youtube.com/watch?v=AShHJdSIxkY

import math
import pyaudio
import struct
import numpy as np
import threading
from colorsys import hls_to_rgb

from SubEngine import *

class Adapter(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.isEnabled = False

        self.fft_data = []
        self.amp_data = []

        self.p = pyaudio.PyAudio()
        self.chunk = 1024
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            input=True,
            output=False,
            frames_per_buffer=self.chunk
        )

    def terminate(self):
        self.isEnabled = False
        self.stream.close()
        self.p.terminate()

    def run(self):
        self.isEnabled = True
        while self.isEnabled:
            data_raw = struct.unpack(str(2 * self.chunk) + 'B', self.stream.read(self.chunk, exception_on_overflow=False))
            self.amp_data = data_raw[:]
            print(np.mean(data_raw))
            data_fft = np.fft.fft(data_raw * np.hanning(len(data_raw)))
            data_fft = np.abs(data_fft)
            data_fft = list(data_fft[0:self.chunk])
            data_fft = map(self.resize, data_fft)
            self.fft_data = data_fft[:]
            print([max(data_fft),max(data_raw)])

    def resize(self, num):
        return (num*2)/self.chunk


class FrSpectrum:

    def __init__(self, output_lenght=450, data_lenght=1024):
        self.output_length = output_lenght
        self.data_length = data_lenght
        self.map = [0] * self.output_length

        a = (3 * (self.data_length-self.output_length)) / ((self.output_length * self.output_length * self.output_length))

        count = 0
        for x in range(self.output_length):
            self.map[x] = round(a * x * x)+1
            count = count +self.map[x]

        if count > data_lenght:
            print("Error in FrSpectrum")
        elif count < data_lenght:
            self.map[self.output_length-1] = self.map[self.output_length-1]+(self.data_length-count)

    def getSpectrum(self, data):
        if len(data) != self.data_length:
            return None

        retVal = [0] * self.output_length

        cursor = 0
        counter = self.map[0]
        buffer = 0
        for i in range(self.data_length):
            counter = counter - 1
            if counter <= 0:
                if buffer == 0:
                    retVal[cursor] = data[i]
                else:
                    retVal[cursor] = round(buffer / self.map[cursor]) 
                if cursor < len(self.map)-1:
                    cursor = cursor + 1
                    counter = self.map[cursor]
            else:
                buffer = buffer + data[i]
        return retVal

class SpecTrain(SubEngine):

    def __init__(self):
        self.build("Train" ,450, 1)
        self.obj = Object()
        self.obj.build(True, 0, [[-1,-1,-1]]*450)

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/Train/enable", str(self.isEnabled)])
        return retVal

    def update(self):
        global adapter
        data = adapter.fft_data[:]
        index = data.index(max(data))
        for i in range(449):
            self.obj.content[450-i] = self.obj.content[449-i]
        if data[index] >= 75:
            val = data[index]
            val = val - 75
            val = float(val) / 2
            val = int(val)
            bri = val
            # 0 - 200 -> 0 - 360
            hue = index
            #0-len -> 0-360
            hue = hue * (360 / len(data))
            self.obj.content[0] = hls_to_rgb(hue, bri, 50)
        else:
            self.obj.content[0] = [0, 0, 0]

    def onMessage(self):
        pass

class WaveSpec(SubEngine):

    def __init__(self):
        self.build("WaveSpec" , 450, 1)
        self.colors = [[-1, -1, -1]]*1020
        self.generateColor()        
        self.spectrum = FrSpectrum()

        self.obj = Object()
        self.obj.build(True,359,[[-1,-1,-1]]*450)
        self.addObj(self.obj)

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/WaveSpec/enable", str(self.isEnabled)])
        return retVal

    def generateColor(self, phase = ([0, 1, 0], [0, 0, -1], [1, 0, 0], [0, -1, 0]), baseColor = [0, 0, 255]):
        pC = 0
        c = 0
        for index in range(len(self.colors)-1):
            c = c + 1
            for i in range(3):
                baseColor[i] = baseColor[i] + phase[pC][i]
                if c == 255:
                    c = 0
                    pC = pC + 1
                self.colors[index] = baseColor[:]
        self.colors[0] = [-1, -1, -1]

    def update(self):
        self.obj.position = self.obj.position + 1
        if self.obj.position >=450:
            self.obj.position = 0
        data = adapter.fft_data[:]
        data = self.spectrum.getSpectrum(data)
        data[0] = 0
        for i in range(450):
            if data[i] >40000:
                data[i] = 30000
            elif data[i] < 15000:
                data[i] = 0
            else:
                data[i] = data[i] - 10000

            self.obj.content[i]= self.colors[int(data[i]/30)]

class Pulse(Object):

    def __init__(self):
        self.build(True,370,[])
        print(self.isVisible)

    def setColor(self, color, rate):
        self.content = []
        for i in range(rate):
            self.content.append(color[:])
            self.content.insert(0, color[:])





class SnakeVibe(SubEngine):

    def __init__(self):
        self.build("SnakeVibe", 450, 1)
        self.pulse = Pulse()
        self.addObj(Pulse)
        self.isEnabled = True

    def update(self):
        pass
    
    def onMessage(self, topic, payload):
        pass

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/SnakeVibe/enable", str(self.isEnabled)])
        return retVal



global adapter
adapter = Adapter()
adapter.daemon = True
adapter.start()
