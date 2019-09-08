import time, datetime, config, BlockLayer, InodeOps, MemoryInterface


MemoryInterface.Initialize_My_FileSystem()
#HANDLE OF BLOCK LAYER
interface = BlockLayer.BlockLayer()

class InodeLayer():

    #PLEASE DO NOT MODIFY THIS
    #RETURNS ACTUAL BLOCK NUMBER FROM RESPECTIVE MAPPING  
    def INDEX_TO_BLOCK_NUMBER(self, inode, index):
        if index == len(inode.blk_numbers): return -1
        return inode.blk_numbers[index]


    #PLEASE DO NOT MODIFY THIS
    #RETURNS BLOCK DATA FROM INODE and OFFSET
    def INODE_TO_BLOCK(self, inode, offset):
        index = offset / config.BLOCK_SIZE
        block_number = self.INDEX_TO_BLOCK_NUMBER(inode, index)
        if block_number == -1: return ''
        else: return interface.BLOCK_NUMBER_TO_DATA_BLOCK(block_number)


    #PLEASE DO NOT MODIFY THIS
    #MAKES NEW INODE OBJECT
    def new_inode(self, type):
        return InodeOps.Table_Inode(type)


    #PLEASE DO NOT MODIFY THIS
    #FLUSHES ALL THE BLOCKS OF INODES FROM GIVEN INDEX OF MAPPING ARRAY  
    def free_data_block(self, inode, index):
        for i in range(index, len(inode.blk_numbers)):
            interface.free_data_block(inode.blk_numbers[i])
            inode.blk_numbers[i] = -1

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


    #IMPLEMENTS WRITE FUNCTIONALITY
    def write(self, inode, offset, data):
        inode.time_modified = str(datetime.datetime.now())[:19] # change time modified
        inode.time_accessed = str(datetime.datetime.now())[:19] # change time accessed
        
        # make sure the inode is not a directory before writing to the blocks.
        if inode.type == config.INODETYPE_FILE:
            self.write_to_offset(offset, data)
        else: return -1
        return 0

    #IMPLEMENTS THE READ FUNCTION 
    def read(self, inode, offset, length):
        inode.time_accessed = str(datetime.datetime.now())[:19] # change time accessed
        return None
    
    #Copy the inputInode's contents to another inode.
    def copy(self, inode):
        return None

    def status(self):
        print(MemoryInterface.status())

if __name__ == '__main__':
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE) # create the inode object of file type
    
    print "CREATION TIME: " + inode.time_created
    print "ACCESS TIME: " + inode.time_accessed
    print "MODIFY TIME: " + inode.time_modified
    print ""
    time.sleep(1)

    InodeLay.write(inode, 0, "Test string") # write to the inode object
    InodeLay.read(inode, 0, 11) # read back the entire string from the inode object

    print "CREATION TIME: " + inode.time_created
    print "ACCESS TIME: " + inode.time_accessed
    print "MODIFY TIME: " + inode.time_modified
   
    InodeLay.status()

