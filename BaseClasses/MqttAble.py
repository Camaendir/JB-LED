from abc import ABC, abstractmethod


class MqttAble(ABC):

    @abstractmethod
    def onMessage(self, mqtttopic, mqttpayload):
        pass

    @abstractmethod
    def getStates(self):
        pass