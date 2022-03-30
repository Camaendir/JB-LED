from BaseClasses.SubEngine import SubEngine
from Cogs.Compression.BlockCompression import BlockCompression


class MqttAble(SubEngine):

    def __init__(self, mqttTopic, name, pixellength, layercount=1, compression=BlockCompression(), resourcesToRegister=()):
        super(MqttAble, self).__init__(name, pixellength, layercount=layercount, compression=compression, resourcesToRegister=resourcesToRegister)
        self.mqttTopic = mqttTopic

    def onMessage(self, mqtttopic, mqttpayload):
        pass
