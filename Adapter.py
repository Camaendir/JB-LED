import pyaudio
import struct
import numpy as np
import threading


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