from multiprocessing import shared_memory


class ResourceAllocation:
    namedictionary = {}

    @staticmethod
    def allocateSharedMemory(name, object_of_size, length):
        shm = shared_memory.ShareableList([object_of_size] * length)
        ResourceAllocation.namedictionary[name] = shm.shm.name

    @staticmethod
    def getSharedMemoryName(name):
        if name not in ResourceAllocation.namedictionary.keys():
            return -1
        return ResourceAllocation.namedictionary[name]