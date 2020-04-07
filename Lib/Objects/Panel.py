class Panel:

    def __init__(self):
        self.transparent = [-1 ,-1 ,-1]
        self.position = 0
        self.isVisible = True 
        self.content = []

        self.kernelContent = []

        self.isMirrored = False
        self.isLooped = False
        self.isRepeated = False
        self.repeats = 0

    def setContent(self, pContent):
        self.kernelContent = pContent[:]
        self.processing()

    def stayMirrored(self, pBoolean):
        self.isMirrored = pBoolean
        self.processing()

    def stayRepeated(self, pBoolean, pNum):
        if pNum > 0 and pBoolean:
            self.isRepeated = True
            self.repeats = pNum
        else:
            self.isRepeated = False
            self.repeats = 0
        self.processing()

    def stayLooped(self, pBoolean):
        self.isLooped = pBoolean
        self.processing()

    def shift(self, pixel=[-1,-1,-1]):
        #lastPixel = self.kernelContent[len(self.kernelContent) - 1]
        lastPixel = self.kernelContent.pop()
        if self.isLooped:
            self.kernelContent.insert(0, lastPixel)
        else:
            self.kernelContent.insert(0, pixel)
        self.processing()

    def insert(self, index, pixel):
        self.kernelContent.insert(index, pixel)
        self.processing()

    def replace(self, index, pixel):
        self.kernelContent[index] = pixel
        self.processing()

    def processing(self):
        newContent = self.kernelContent[:]

        # Mirror
        if self.isMirrored:
            for i in range(len(self.kernelContent) - 1, -1, -1):
                newContent.append(self.kernelContent[i])

        # Repeat
        if self.isRepeated:
            newContent = newContent * self.repeats

        # Push to Content
        self.content = newContent
