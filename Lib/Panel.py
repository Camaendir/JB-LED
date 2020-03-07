class Panel:
    global transparent

    def __init__(self):i
        transparent = [-1 ,-1 ,-1]
        self.position = 0;
        self.isVisible = False
        self.content = []

        self.kernelContent = []

        self.isMirrowed = False
        self.isLooped = False
        self.isRepeated = False
        self.repeats = 0

    def setContent(self, pContent):
        self.kernelContent = pContent[:]
        self.processing()

    def stayMirrored(self, pBoolean):
        self.isMirrowed = pBoolean
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

    def shift(self, pixel=transparent):
        lastPixel = self.kernelContent[len(self.kernelContent) - 1]
        self.kernelContent.remove(lastPixel)
        if self.isLooped:
            self.kernelContent.insert(0, lastPixel)
        else:
            self.kernelContent.insert(0, pixel)

    def insert(self, index, pixel):
        self.kernelContent.insert(index, pixel)
        self.processing()

    def replace(self, index, pixel):
        self.kernelContent[index] = pixel
        self.processing()

    def processing(self):
        newContent = self.kernelContent[:]

        # Mirror
        if self.isMirrowed:
            for i in range(len(self.kernelContent) - 1, -1, -1):
                newContent.append(self.kernelContent[i])

        # Repeat
        if self.isRepeated:
            newContent = newContent * self.repeats

        # Push to Content
        self.content = newContent
