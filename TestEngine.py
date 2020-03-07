from Biblio.Engine import Engine
from Biblio.SubEngine import SubEngine
from Biblio.Object import Object

class Test(SubEngine):

    def __init__(self, mqtt):
        self.build(mqtt,450,3)
        self.obj = Object()
        self.obj.build(True,0,[[255,255,255]]*450)
        self.addObj(self.obj,2)

    def update(self):
        if self.obj.content[0] == [0,0,0]:
            self.obj.content = [[255,255,255]]*450
        else:
            self.obj.content = [[0,0,0]]*450


#def compFrame(pFrame):
#    block = []
#    currentBlock = 0
#    lastPixel = pFrame.pop(0)
#    for pixel in pFrame:
#        if lastPixel == pixel:
#            if currentBlock >= 254:
#                block.append([currentBlock, lastPixel])
#                currentBlock = 0
#            else:
#                currentBlock = currentBlock + 1
#        else:
#            block.append([currentBlock,lastPixel])
#            currentBlock = 0
#            lastPixel = pixel
#    block.append([currentBlock,lastPixel])
#    retVal = []
#    for b in block:
#        retVal = rowToBits(b)
#    return retVal


#def rowToBits(pRow):
#    if pRow[1] == [-1, -1, -1]:
#        retVal = (255 << 24) + pRow[0]
#    else:
#        retVal = (pRow[0] << 24) + (pRow[1][0] << 16) + (pRow[1][1] << 8) + pRow[1][2]
#    return retVal


#def bitToRow(pBits):
#    retVal = [0, [0, 0, 0]]
#    retVal[0] = (pBits & 4278190080) >> 24
#    if retVal[0] == 255:
#        retVal[0] = pBits & 255
#        retVal[1] = [-1, -1, -1]
#    else:
#        retVal[1][0] = (pBits & 16711680) >> 16
#        retVal[1][1] = (pBits & 65280) >> 8
#        retVal[1][2] = pBits & 255
#    return retVal


if __name__ == '__main__':
    eng = Engine()
    eng.addSubEngine(Test('abc'), True)
    eng.run()
