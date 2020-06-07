import BlockLayer, sys, config, MemoryInterface

MemoryInterface.Initialize_My_FileSystem()
interface = BlockLayer.BlockLayer()


class Operations():	
    def __init__(self):
        self.map = []

    #WRITES STRING1
    def write(self, string):
        data_array = []
        
        # verify that string is of type string
        for i in range(0, len(string), config.BLOCK_SIZE):
            
            # divide up the string into chunks of length BLOCK_SIZE
            data_array.append(string[i : i + config.BLOCK_SIZE])

        self.__write_to_filesystem(data_array)


    #READS THE STRING
    def read(self):
        data = []
        
        for i in range(len(self.map)):
            # index through block numbers in map to get data blocks
            
            data.append(interface.BLOCK_NUMBER_TO_DATA_BLOCK(self.map[i]))
        
        print( "".join(data))           
        return "".join(data)

    #WRITE TO FILESYSTEM
    def __write_to_filesystem(self, data_array):
        for i in range(len(data_array)):
            valid_block_number = interface.get_valid_data_block()
            interface.update_data_block(valid_block_number, data_array[i])
            self.map.append(valid_block_number)

    #STATUS FUNCTION TO CHECK THE STATUS OF THE DATA BLOCKS IN THE MEMORY
    def status(self):
        print(MemoryInterface.status())

    '''
    FUNCTION:
        write_to_offset

    SUMMARY:
        If valid data is stored at offset, the function overwrites
        the storage beginning at the offset with the contents of string.
        
    RETURN:
        0 => if storage was successful.
        1 => if the offset does not contain valid data.
    '''
    def write_to_offset(self,offset,string):	

        # Write data to a freshly allocated block of memory. Free up
        # space if required.
        def NESTED_write_filesystem_map(nDeallocateIdx, nDataList):
            nBlockNum = interface.get_valid_data_block() # allocate new block
            interface.update_data_block(nBlockNum, ''.join(nDataList)) # write to the new block

            # if the string is being replaced, update the blockNumber and deallocate old block. 
            # Otherwise, add the blockNumber to the end of the file.
            if nDeallocateIdx < len(self.map):
                interface.free_data_block( self.map[nDeallocateIdx] ) # old block
                self.map[nDeallocateIdx] = nBlockNum # replace file contents
            else:
                self.map.append(nBlockNum)

        # Output list either contains data from the indexed map's blocks -- or all NULL values
        # to represent a freshly initialized block.
        def NESTED_get_init_block_list(nBlockIdx):
            if nBlockIdx < len(self.map):
                return list(interface.BLOCK_NUMBER_TO_DATA_BLOCK(self.map[nBlockIdx]))
            else:
                return ['\0' for i in range(config.BLOCK_SIZE)]
       
        # Locate the index of the block number in the self.map referenced by the input offset.
        iBlock = 0 # block index for the self.map list
        while offset >= config.BLOCK_SIZE:
            offset -= config.BLOCK_SIZE
            iBlock += 1

        # Read the current data stored at the block.
        blockList = NESTED_get_init_block_list(iBlock)

        # Check if offset contains valid data before overwriting.
        # Otherwise, return an error.
        if blockList.count('\0') < config.BLOCK_SIZE:
            
            charCnt = 0 # input string indexer
            while charCnt < len(string):

                # Write the current blockList to the selectified block.
                # If the block offset exceeds a width of 4, the next 4
                # string characters should go into the next available block.
                if offset > config.BLOCK_SIZE-1:
                    offset = 0
                    NESTED_write_filesystem_map(iBlock, blockList)
                    iBlock += 1 # go to the next 4 characters of the file
                    blockList = NESTED_get_init_block_list(iBlock) 

                # Replace the next offset value with the string contents.
                blockList[offset] = string[charCnt]
                offset += 1 # next index for the block
                charCnt += 1 # next index for the new string
            
            NESTED_write_filesystem_map(iBlock, blockList)
            return 0

        else:
            return -1

if __name__ == "__main__":
    if len(sys.argv) < 3: 
        print("Usage: python HW1.py <string1> <string2>")
        exit(0)
    test = Operations()
    test.write(sys.argv[1])
    test.read()
    test.status()
    test.write_to_offset(int(sys.argv[3]),sys.argv[2])
    test.read()
    # last call 
    test.status()

