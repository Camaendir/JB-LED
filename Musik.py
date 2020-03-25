#Basierend auf https://www.youtube.com/watch?v=AShHJdSIxkY

import pyaudio
import struct
import numpy as np
import threading
from colorsys import hls_to_rgb
import time
from Lib.SubEngine import *
from Lib.Objects.Object import Object
from Lib.Objects.Panel import Panel

class Adapter(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.isEnabled = False
        self.raw_data = []
        self.fft_data = []
        self.amp_data = []
        self.p = pyaudio.PyAudio()
        self.chunk = 1024
        self.offset = [0]*self.chunk
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            input=True,
            output=False,
            frames_per_buffer=self.chunk
        )
        self.offsetrange = []

    def terminate(self):
        self.isEnabled = False
        self.stream.close()
        self.p.terminate()

    def run(self):
        self.isEnabled = True
        print("Bitte leise sein")
        for i in range(50):
            raw = struct.unpack(str(2*self.chunk)+ 'B', self.stream.read(self.chunk, exception_on_overflow=False))
            print("it works")
            ad = raw[:]
            fft = np.fft.fft(raw)
            print("see")
            fft = np.abs(fft)
            fft = list(fft[0:self.chunk])
            fft = map(self.resize, fft)
            self.offsetrange.append(fft)
        for i in range(self.chunk):
            full = 0
            for j in range(len(self.offsetrange)):
                full = full + self.offsetrange[j][i]
            self.offset[i] = float(full) / len(self.offsetrange)
        print("Kannst wieder laut sein")
        while self.isEnabled:
            data_raw = struct.unpack(str(2 * self.chunk) + 'B', self.stream.read(self.chunk, exception_on_overflow=False))
            self.amp_data = data_raw[:]
            data_fft = np.fft.fft(data_raw) # * np.hanning(len(data_raw)))
            data_fft = np.abs(data_fft)
            data_fft = list(data_fft[0:self.chunk])
            data_fft = map(self.resize, data_fft)
            diff = []
            self.raw_data = data_fft[:]
            zip1 = zip(data_fft, self.offset)
            for a,b in zip1:
                diff.append(a-b)
            self.fft_data = diff[:]

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
        self.adapter = Adapter()
        self.shift = 180
        self.adapter.daemon = True
        self.stated = False
        self.build("Train" ,450, 1)
        self.obj = Panel()
        self.obj.stayMirrored(True)
        self.obj.position = 245
        self.obj.setContent([[0,0,0]]*225)
        #self.obj.build(True, 0, [[-1,-1,-1]]*450)
        self.addObj(self.obj)
        self.First = 0
        self.bufferlength = 11
        self.buffer = [[0,0,0]]*self.bufferlength
        self.gauss = (41,26,16,7,4,1)
        self.buffermid = int((self.bufferlength-1)/2)
        self.gaussaverage = self.gauss[0]
        for i in range(self.buffermid):
            self.gaussaverage = self.gaussaverage +(2* self.gauss[1+i])

    def getStates(self):
        retVal = []
        retVal.append(["strip/info/Train/enable", str(self.isEnabled)])
        return retVal

    def update(self):
        if not self.stated:
            self.adapter.start()
            time.sleep(7)
            self.stated = True
        data = self.adapter.fft_data[:]
        data = data[10:30]
        index = data.index(max(data))
        frame = [-1,0]
        if data[index] >= 15:
            #print("over")
            val = data[index]
            val = val - 7
            val = float(val) / 2
            val = int(val)
            bri = 1.0
            hue = index
            hue = float(hue) / len(data)
            frame = [hue, 1]
        else:
            pass
            #print(data[index])
        #print("frame: " + str(frame))
        self.buffer[0] = frame
        together = 0
        full_value = []
        for i in range(self.bufferlength):
            gaussindex = self.gauss[abs(i-self.buffermid)]
            if(self.buffer[i][0] > -1):
                together = together + gaussindex
                full_value.append((self.buffer[i][0] * gaussindex, 0.5*gaussindex))
            else:
                full_value.append((0,0))
        fin = [0,0]
        for elm in full_value:
            fin[0] = fin[0] + elm[0]
            fin[1] = fin[1] + elm[1]
        together = max(together, 1)
        fin[0] = float(fin[0]) / together
        fin[1] = float(fin[1]) / self.gaussaverage
        #print(fin)
        #print("buffer : " + str(self.buffer))
        if(fin[1] < 0.1):
            fin[1] = 0
        final = hls_to_rgb((fin[0] + self.shift) % 360, fin[1], 1)
        final = [int(i * 255) for i in final]
        self.obj.shift(final)
        for i in range(self.bufferlength - 1):
            self.buffer[self.bufferlength - 1 -i] = self.buffer[self.bufferlength - 2 - i]


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



