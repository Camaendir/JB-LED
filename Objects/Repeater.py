import copy
from math import floor

from Objects.Object import Object


class Repeater(Object):

    def __init__(self, isVisible, position, content, pixellength, numRepeats=-1, spacing=0):
        super().__init__(isVisible, position, content)
        self.numRepeats = numRepeats
        self.spacing = spacing
        self.pixellength = pixellength

    def getContent(self):
        max_reps = floor(self.pixellength / (len(self.content) + self.spacing))
        reps = max_reps if self.numRepeats == -1 else min(self.numRepeats, max_reps)
        full = copy.deepcopy(self.content)
        full.extend([[-1,-1,-1]]*self.spacing)
        return full * reps
