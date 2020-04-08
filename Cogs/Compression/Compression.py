from abc import ABC, abstractmethod


class Compression(ABC):

    @abstractmethod
    def compressFrame(self, frame):
        pass

    @abstractmethod
    def decompressFrame(self, frame):
        pass