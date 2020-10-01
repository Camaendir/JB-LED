import abc
import time
from abc import ABC
from multiprocessing import shared_memory
import threading


class ResourceCreation(ABC):

    def __init__(self, name, object_of_size, length):
        self.running = True
        self.name = name
        self.resource = shared_memory.ShareableList([object_of_size] * length)
        self.pipe = None
        self.lock = None

    def configure(self, pipe, lock):
        self.pipe = pipe
        self.lock = lock

    def setData(self, data, startIndex=0, endIndex=-1, hasIndex=False, Index=None):
        if hasIndex:
            self.lock[Index].acquire()
        else:
            self.lock.acquire()
        max_index = len(self.resource if not hasIndex else self.resource[Index])
        if endIndex == -1 or endIndex > max_index:
            endIndex = max_index
        if startIndex > endIndex or startIndex >= max_index:
            return
        for i in range(endIndex - startIndex):
            index = i + startIndex
            if hasIndex:
                self.resource[Index][index] = int(data[i])
            else:
                self.resource[index] = int(data[i])
        if hasIndex:
            self.lock[Index].release()
        else:
            self.lock.release()

    def runEntry(self):
        threading.Thread(target=self.pipeManager).start()
        self.setup()
        while self.running:
            try:
                self.run()
            except KeyboardInterrupt:
                self.running = False
                self.terminate()
                if isinstance(self.name, str):
                    self.resource.shm.close()
                    self.resource.shm.unlink()
                else:
                    for key in self.resource.keys():
                        self.resource[key].shm.close()
                        self.resource[key].shm.unlink()

    def pipeManager(self):
        while True:
            time.sleep(0.5)
            if self.pipe is None:
                continue
            if self.pipe.poll():
                if self.pipe.recv() == "t":
                    self.running = False
                    self.terminate()
                    if isinstance(self.name, str):
                        self.resource.shm.close()
                        self.resource.shm.unlink()
                    else:
                        for key in self.resource.keys():
                            self.resource[key].shm.close()
                            self.resource[key].shm.unlink()
                    print("Resource terminated")
                    break

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def terminate(self):
        pass
