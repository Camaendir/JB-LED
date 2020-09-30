from abc import abstractmethod


class Object:

    def __init__(self, isVisible, position, content):
        self.isVisible = isVisible
        self.position = position
        self.content = content

    @abstractmethod
    def getContent(self):
        return self.content
