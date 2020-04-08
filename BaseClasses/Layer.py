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
        field = []
        for i in range(self.pixellength):
            field.append(self.transparent)
        for obj in self.objList:
            if obj.isVisible:
                for i in range(len(obj.content)):
                    index = obj.position - i
                    if index < 0:
                        index = self.pixellength + index
                    field[index] = obj.content[i]
        return field
