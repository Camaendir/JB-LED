class ResourceProcess:
    def __init__(self, shmName, process, pipeParent, lock):
        self.process = process
        self.pipeParent = pipeParent
        self.lock = lock
        self.shmName = shmName
