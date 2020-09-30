from Resources.ResourceAllocation import ResourceAllocation
from multiprocessing import shared_memory


class ResourceAccess:

    def __init__(self, name):
        mem_name = ResourceAllocation.getSharedMemoryName(name)
        if mem_name == -1:
            raise Exception("Cant access Resource. Resource with name '" + name + "' does not exist")
        self.resource = shared_memory.ShareableList(name=mem_name)

    def getData(self, startindex=0, endindex=-1):
        max_index = len(self.resource)
        if endindex == -1 or endindex > max_index:
            endindex = max_index
        if startindex > endindex or startindex > max_index:
            return None
        return [a for a in self.resource][startindex:endindex]
