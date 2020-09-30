class Layer:

    def __init__(self, pixellength):
        self.objList = []
        self.pixellength = pixellength
        self.transparent = [-1, -1, -1]

    def addObj(self, obj):
        self.objList.append(obj)

    def delObj(self, obj):
        self.objList.remove(obj)

    def getFrame(self):
        field = [self.transparent] * self.pixellength

        for obj in self.objList:
            if not obj.isVisible:
                continue
            content = obj.getContent()
            for i in range(len(content)):
                index = obj.position + i
                if index < 0:
                    index = self.pixellength + index
                elif index >= self.pixellength:
                    while index >= self.pixellength:
                        index -= self.pixellength
                if content[i] != self.transparent:
                    field[index] = content[i]
        return field
