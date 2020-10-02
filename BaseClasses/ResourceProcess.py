class ResourceProcess:
    def __init__(self, shmName, process, pipeParent, lock):
        self.process = process
        self.pipeParent = pipeParent
        self.lock = lock
        self.shmName = shmName

    def terminate(self):
        if self.pipeParent is not None:
            self.pipeParent.send("t")
        if self.process is not None and self.process.is_alive:
            self.process.join()
            self.pipeParent.close()
