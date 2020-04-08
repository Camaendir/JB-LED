from Cogs.Compression.Compression import Compression


class BlockCompression(Compression):

    def compressFrame(self, pFrame):
        block = []
        currentBlock = 0
        lastPixel = pFrame.pop(0)
        for pixel in pFrame:
            if lastPixel == pixel:
                if currentBlock >= 254:
                    block.append([currentBlock, lastPixel])
                    currentBlock = 0
                else:
                    currentBlock = currentBlock + 1
            else:
                block.append([currentBlock, lastPixel])
                currentBlock = 0
                lastPixel = pixel
        block.append([currentBlock, lastPixel])
        retVal = []
        for b in block:
            retVal.append(self.rowToBits(b))
        return retVal

    def decompressFrame(self, pFrame):
        block = []
        for data in pFrame:
            block.append(self.bitToRow(data))
        retVal = []
        for row in block:
            retVal = retVal + [row[1]] * (row[0] + 1)
        return retVal

    @staticmethod
    def rowToBits(pRow):
        if pRow[1] == [-1, -1, -1]:
            retVal = (255 << 24) + pRow[0]
        else:
            retVal = (pRow[0] << 24) + (pRow[1][0] << 16) + (pRow[1][1] << 8) + pRow[1][2]
        return retVal

    @staticmethod
    def bitToRow(pBits):
        retVal = [0, [0, 0, 0]]
        retVal[0] = (pBits & 4278190080) >> 24
        if retVal[0] == 255:
            retVal[0] = pBits & 255
            retVal[1] = [-1, -1, -1]
        else:
            retVal[1][0] = (pBits & 16711680) >> 16
            retVal[1][1] = (pBits & 65280) >> 8
            retVal[1][2] = pBits & 255
        return retVal
