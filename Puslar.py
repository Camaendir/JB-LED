from Lib.Object import Object
from Lib.SubEngine import SubEngine
from Adapter import Adapter
import time

class Pulsar(SubEngine):

    def __init__(self, basefreqs=((10,15), (15,25), (25,35)), basecolors=((255,0,0), (0,255,0), (0,0,255)), middle=190, min_width=(50,25,2), max_width=(200, 120, 50), meteor_pro_width=7, deflection=(2,1,0.5)):
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
        self.meteor_line = meteor_pro_width
        self.deflection = deflection
        #self.METEORS = []
        #for i in range(10):
            #self.METEORS.append(Meteor())
        self.last = [0] * self.layercount
        for i in range(self.layercount):
            Obj = Pusle(middle, basecolors[i])
            self.objects.append(Obj)
            self.addObj(Obj, len(basecolors)-i)


    def getStates(self):
        return []

    def update(self):
        if not self.started:
            self.adapter.start()
            time.sleep(5)
        fftdata = self.getFFTData()
        for i in range(self.layercount):
            max_data = max(fftdata[self.frequencies[i][0]:self.frequencies[i][1]])
            # Needs tweaking
            width = self.min_width[i] + self.deflection[i] * max_data
            self.objects[i].update(width)
            if not self.started:
                self.last[i] = width
            if width > self.max_width[i] or width > (self.last[i] * (100+self.meteor_line[i])/100):
                #self.METEOR(i, width, width - self.last[i])
                print("Meteor")

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
        self.content = [self.color]*width
        # Weichzeichner
