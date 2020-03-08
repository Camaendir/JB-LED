from Lib.Object import Object
from Lib.SubEngine import SubEngine
from Adapter import Adapter
import time

class Pulsar(SubEngine):

    def __init__(self, basefreqs=((10,13), (15,25), (30,35)), basecolors=((0,0,255), (0,255,0), (255,0,0)), middle=190, min_width=(50,30,20), max_width=(160, 120, 80), deflection=(2,1,0.5), escape_velocity=(40, 20, 10)):
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
        self.escapevelocity = escape_velocity
        self.lasting = []
        for defl in min_width:
            self.lasting.append([[defl]*3])
        #self.METEORS = []
        #for i in range(10):
            #self.METEORS.append(Meteor())
        self.last = [0] * self.layercount
        for i in range(self.layercount):
            Obj = Pusle(middle, basecolors[i])
            self.objects.append(Obj)
            self.addObj(Obj, len(basecolors)-1-i)


    def getStates(self):
        return []

    def update(self):
        if not self.started:
            self.adapter.start()
            time.sleep(7)
        fftdata = self.getFFTData()
        for i in range(self.layercount):
            max_data = max(fftdata[self.frequencies[i][0]:self.frequencies[i][1]])
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
            if width > self.last[i] + self.escapevelocity[i]:
                auslenkung = width
                speed = width - self.last[i]
                print("Meteor" + str(i))
            else:
                width = min(width, self.last[i] + 10)

            self.lasting[i][0][0] = width
            self.last[i] = width
            self.objects[i].update(width)
        if not self.started:
            self.started = True


    def onMessage(self, topic, payload):
        pass

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

    def __init__(self, position, color):
        self.build(True, position, [[-1, -1, -1]]*225)
        self.color = color

    def update(self, width):
        self.content = [self.color]*int(width)
        # Weichzeichner
