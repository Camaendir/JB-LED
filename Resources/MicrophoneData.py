import time
import numpy as np
from Resources.ResourceCreation import ResourceCreation
import struct
import pyaudio
from multiprocessing import shared_memory


class MicrophoneData(ResourceCreation):

    def __init__(self):
        self.chunk = 1024
        self.fftBuffer = int(48000/10)
        self.running = True
        self.resource = {"audio": shared_memory.ShareableList([1] * self.chunk*2),
                         "fft": shared_memory.ShareableList([300.0] * 2000)}
        self.name = ("audio", "fft")
        self.p = None
        self.stream = None

    def setup(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=48000,
                                  input=True,
                                  output=False,
                                  frames_per_buffer=self.fftBuffer)

    def run(self):
        fr = time.time()
        raw_audio_data = struct.unpack(str(2 * self.fftBuffer) + 'B',
                                       self.stream.read(self.fftBuffer, exception_on_overflow=False))
        self.setData(raw_audio_data[-2*self.chunk:], hasIndex=True, Index="audio")

        hann = np.hanning(len(raw_audio_data))
        fft = np.fft.fft(np.multiply(raw_audio_data, hann))
        fft = list(np.multiply(2.0, np.multiply(1/self.fftBuffer, np.abs(fft)[:self.fftBuffer])))
        self.setData(fft[:2000], hasIndex=True, Index="fft")

        fr = time.time() - fr
        if fr <= 0.05:
            time.sleep(0.05 - fr)

    def terminate(self):
        pass