from Resourcen.WIP.Adapter import Adapter
import time
from colorsys import hls_to_rgb, rgb_to_hls
from Objects.Object import Object
from BaseClasses.SubEngine import SubEngine


class Pulsar(SubEngine):

    def __init__(self, basefreqs=((5,8), (20,30), (40,50)), basecolors=((0,0,255), (0,255,0), (255,0,0)), middle=244, min_width=[0,0,5], max_width=(160, 120, 80), deflection=(2,1.5,1), escape_velocity=(200, 80, 30), max_deflection = (5, 2, 1), party=False):
        if len(basefreqs) is not len(basecolors) or len(min_width) is not len(max_width) or len(max_width) is not len(deflection) or len(deflection) is not len(basecolors):
            print("Array sizes not matching")
            return
        self.adapter = Adapter()
        self.adapter.daemon = True
        self.build("Pulsar", 450, len(basefreqs))
        self.objects = []
        self.started = False
        self.layercount = len(basecolors)
        self.colors = basecolors
        self.frequencies = basefreqs
        self.max_width = max_width
        self.min_width = min_width
        self.deflection = deflection
        if not party:
            escape_velocity = [int(i / 2) for i in escape_velocity]
        self.escapevelocity = escape_velocity
        self.lasting = []
        self.position = middle
        self.max_deflection = max_deflection
        for defl in min_width:
            self.lasting.append([[defl]*7])
        #self.METEORS = []
        #for i in range(10):
            #self.METEORS.append(Meteor())
        self.last = [0] * self.layercount
        self.obj = Object()
        self.mirror = Object()
        self.mirror.build(True, 450, [[-1,-1,-1]]*225)
        self.obj.build(True, middle, [[-1,-1,-1]]*225)
        self.addObj(self.obj, 0)
        self.addObj(self.mirror, 1)


    def getStates(self):
        return []

    def update(self):
        if not self.started:
            self.adapter.start()
            time.sleep(7)
        fftdata = self.getFFTData()
        sum_fft = 0
        for a in fftdata:
            sum_fft = sum_fft + a
        avg_fft = sum_fft / len(fftdata)
        for i in range(self.layercount):
            max_data = max(fftdata[self.frequencies[i][0]:self.frequencies[i][1]])
            max_data = max_data - avg_fft
            # Needs tweaking
            width = min(self.min_width[i] + (self.deflection[i] - (self.last[i]/100)) * max_data, self.max_width[i])
            if not self.started:
                self.last[i] = width
            sum = width
            for a in self.lasting[i]:
                sum = sum + a[0]
            avg = sum / (len(self.lasting[i]) + 1)
            width = avg
            for j in range(len(self.lasting[i]) - 1):
                self.lasting[i][j + 1][0] = self.lasting[i][j][0]
            #if i is 0:
            #    print("-"*max(0,int((width - self.last[i]) / 2)))
            if width > self.last[i] + self.escapevelocity[i]:
                auslenkung = width - (self.escapevelocity[i]/2)
                speed = width - self.last[i]
                width = width - (self.escapevelocity[i] / 2)
                print("Meteor" + str(i))
            else:
                width = min(width, self.last[i] + self.max_deflection[i])

            self.lasting[i][0][0] = width
            self.last[i] = width
            if i is not 0:
                self.min_width[i-1] = width + 2
        if not self.started:
            self.started = True
        content = [[-1,-1,-1]]*225
        for i in range(self.layercount):
            for j in range(int(self.last[i])):
                content[j] = self.colors[i]
        content = self.gaussblurr(content)
        self.obj.content = content
        self.mirror.content = list(reversed(content[:]))[225 - (450 - self.position):225]


    def onMessage(self, topic, payload):
        pass

    def gaussblurr(self, content, width=2):
        final = []
        gauss = (41, 26, 16, 7, 4, 1)
        gausssum = gauss[0]
        for i in range(len(content)):
            color = [max(0,d) * gauss[0] for d in content[i]]
            for j in range(width):
                j = j+1
                gausssum = gausssum + (gauss[j] * 2)
                #print('+:' + str(i+j) + ' -: ' + str(i-j) + ' len: ' + str(len(content)))
                zp = zip([ max(0,d) * gauss[j] for d in content[min(len(content)-1, i + j)][:]], color[:], [max(0,d) * gauss[j] for d in content[max(0, i - j)][:]])
                #print(zp)
                color = []
                for a, b, c in zp:
                    color.append(a+b+c)
            final_color = []
            for a in color:
                final_color.append(min(255, max(0, int(a / gausssum))))
            final.append(final_color)
        for i in range(len(final)):
            hls = rgb_to_hls(float(final[i][0]) / 255, float(final[i][1]) / 255, float(final[i][2] )/ 255)
            final[i] = [int(a * 255) for a in hls_to_rgb(hls[0], hls[1], 1)]
        return final

    #def METEOR(self, layerindex, width, speed):
    #    for met in self.METEORS:
    #        if met.isFree:
    #            met.spawn(color=self.colors[i], width=width, speed=speed)
    #            return
    #    met = Meteor()
    #    self.addObj(met.getObject(), self.layercount - layerindex)
    #    self.METEORS.append(met)
    #    met.spawn(color=self.colors[i], width=width, speed=speed)

    def getFFTData(self):
        return self.adapter.fft_data[:]



class Pusle(Object):

    def __init__(self, position, color, nextcolor):
        self.build(True, position, [[-1, -1, -1]]*225)
        self.color = color
        self.gauss = (41, 26, 16, 7, 4, 1)
        self.nextcolor = nextcolor

    def update(self, width):
        if gauswidth > len(gauss):
            print("Error")
            return
        self.content = [self.color]*int(width)
