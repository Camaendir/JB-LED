class EngineProcess:

    def __init__(self, subengine, name, process, parent, isEnabled, isCompressed, compressor, startPixel, mqttTopic):
        self.subengine = subengine
        self.name = name
        self.process = process
        self.isEnabled = isEnabled
        self.parent = parent
        self.isCompressed = isCompressed
        self.compressor = compressor
        self.startPixel = startPixel
        self.isMqtt = mqttTopic is not None
        self.mqttTopic = mqttTopic
    
    def terminate(self):
        if not self.isEnabled:
            self.parent = None
            self.process = None
            return
        if self.parent is not None:
            self.parent.send("t")
        if self.process is not None and self.process.is_alive:
            self.process.join()
            self.parent.close()
            self.process = None
            self.parent = None
            self.isEnabled = False
