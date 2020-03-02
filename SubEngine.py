class Layer:

    def build(self, pixellength=450):
        self.objList = []
        self.pixellength = pixellength
        self.transparent = (-1,-1,-1)

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

class SubEngine:

    def build(self, mqtttopic, pixellength, layercount):
        self.layList = []
        self.mqttTopic = mqtttopic
        self.isEnabled = False 
        self.pixellength = pixellength
        self.transparent = (-1,-1,-1)

        for i in range(layercount):
            tmp = Layer()
            tmp.build()
            self.layList.append(tmp)

    def addObj(self, obj,layer=0):
        self.layList[layer].addObj(obj)

    def delObj(self, obj):
        for layer in self.layList:
            layer.delObj(obj)

    def getFrame(self):
        plain = []
        for i in range(self.pixellength):
            plain.append(self.transparent)

        frames = []
        for i in range(len(self.layList)):
            frames.append(self.layList[i].getFrame())

        for i in range(len(frames)):
            for j in range(self.pixellength):
                if plain[j]==self.transparent and frames[i][j]!=self.transparent:
                    plain[j] = frames[i][j]
        return plain    

    def on_message(self, topic, payload):
        if topic == "enable":
            print([topic,payload])
            self.isEnabled = payload.lower() in ("true", "t", "1", "on") 
        self.onMessage(topic, payload)
        


class Object:

    def build(self, isVisible, position, content):
        self.isVisible = isVisible
        self.position = position
        self.content = content
