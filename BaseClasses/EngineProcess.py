class EngineProcess:

    def __init__(self, subengine, name, process, parent, isEnabled, isCompressed, compressor):
        self.subengine = subengine
        self.name = name
        self.process = process
        self.isEnabled = isEnabled
        self.parent = parent
        self.isCompressed = isCompressed
        self.compressor = compressor
