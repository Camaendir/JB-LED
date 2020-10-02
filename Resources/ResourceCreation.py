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

    def setData(self, data, start_index=0, end_index=-1, hasIndex=False, Index=None):
        if hasIndex:
            self.lock[Index].acquire()
        else:
            self.lock.acquire()
        max_index = len(self.resource if not hasIndex else self.resource[Index])
        if end_index == -1 or end_index > max_index:
            end_index = max_index
        if start_index > end_index or start_index >= max_index:
            return
        for i in range(end_index - start_index):
            index = i + start_index
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
                self.terminating()

    def terminating(self):
        self.running = False
        self.terminate()

        if isinstance(self.name, str):
            self.resource.shm.close()
            try:
                self.resource.shm.unlink()
            except FileNotFoundError:
                pass
        else:
            for key in self.resource.keys():
                self.resource[key].shm.close()
                try:
                    self.resource[key].shm.unlink()
                except FileNotFoundError:
                    pass

    def pipeManager(self):
        while True:
            time.sleep(0.5)
            if self.pipe is None:
                continue
            if self.pipe.poll():
                if self.pipe.recv() == "t":
                    self.terminating()
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
