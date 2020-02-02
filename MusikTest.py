import math
import numpy as np
from scipy.fftpack import fft


def lengthVector( num):
    return math.sqrt(num.real * num.real + num.imag * num.imag)

data_raw = np.sin(2*np.pi*500*np.arange(0,1,0.00002083))


data_fft = fft(data_raw)
data_fft = map(complex,data_fft)
data_fft = map(lengthVector,data_fft)

fr = (48000/2) * np.linspace(0,1,1024)
fr = map(complex, fr)
fr = map(lengthVector,fr)
data = []
for i in range(len(fr)):
    data.append([fr[i],data_fft[i]])
    if data_fft[i]>0.7:
        print([data[i],i])

