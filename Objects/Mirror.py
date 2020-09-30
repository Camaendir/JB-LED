import copy
from Objects.Object import Object


class Mirror(Object):

    def __init__(self, isVisible, position, content, isMirrored=True, isMirrorToRight=True):
        super(Mirror, self).__init__(isVisible, position, content)
        self.initialPosition = position
        self.isMirrored = isMirrored
        self.isMirrorToRight = isMirrorToRight

    def getContent(self):
        if self.isMirrorToRight:
            full_content = self.content
            rev = copy.deepcopy(self.content)
            rev.reverse()
            return full_content + rev
        else:
            self.position = self.initialPosition - len(self.content)
            rev = copy.deepcopy(self.content)
            rev.reverse()
            full_content = rev
            return full_content + self.content
