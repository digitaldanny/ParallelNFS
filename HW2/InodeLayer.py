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
    SUMMARY: write
    This function writes characters of a string to blocks pointed at 
    by the inode.blk_numbers.
    '''
    def write(self, inode, offset, data):
        inode.time_modified = str(datetime.datetime.now())[:19] # change time modified
        inode.time_accessed = str(datetime.datetime.now())[:19] # change time accessed
        
        # make sure the inode is not a directory before writing to the blocks.
        if inode.type == config.INODETYPE_FILE:
            # If file is a block, overwrite data beginning at the offset.
            fileSizeError = self.__write_to_offset(inode, offset, data)
            
            # if writing from an offset too large for the file size, return an error.
            if fileSizeError: return -1
            
        else: return -1 # attempting to write to a directory
        
        return inode # updated inode returned

    '''
    SUMMARY: read
    This function reads up to "length" bytes starting form the offset
    from blocks indexed by the inode objects.
    '''
    def read(self, inode, offset, length):
        # change time accessed
        inode.time_accessed = str(datetime.datetime.now())[:19]
        
        # go through all blocks until number of requested bytes are read.
        data = []
        for i in range(len(inode.blk_numbers)):
            if inode.blk_numbers[i] != -1: # only continues to check blocsk if the current block is defined
                block = interface.BLOCK_NUMBER_TO_DATA_BLOCK(inode.blk_numbers[i]) # next 512 bytes of data
                
                if (offset + length) <= config.BLOCK_SIZE: # end of the read
                    # if the rest of the bytes requested are located in the current
                    # block, enter.
                    end = offset + length
                    data.append(block[offset:end])
                    break
                
                else:
                    # if the requested bytes continue into the next block, set up
                    # the offset and length for the next block.
                    length -= (config.BLOCK_SIZE - offset)
                    end = offset + config.BLOCK_SIZE - offset
                    data.append(block[offset:end])               # append the next chunk of the read data
                    offset = 0                                   # beginning of the next block
                    
            else: return -1 # error: block number not valid
        print( "".join(data))           
        return (inode, "".join(data)) # returns a tuple of read data and the updated inode
    
    #Copy the inputInode's contents to another inode.
    def copy(self, inode):
        return None

    def status(self):
        print(MemoryInterface.status())
        
    '''
    FUNCTION:
        __write_to_offset

    SUMMARY:
        If valid data is stored at offset, the function overwrites
        the storage beginning at the offset with the contents of string.
        
    RETURN:
        0 => if storage was successful.
        1 => if the offset does not contain valid data.
    '''
    def __write_to_offset(self, inode, offset, string):	

        # NESTED FUNCTIONS ----------------------------------------------------
        
        # Write data to a freshly allocated block of memory. Free up
        # space if required.
        def NESTED_write_filesystem_map(nDeallocateIdx, nDataList):

            # if the string is being replaced, update the blockNumber and deallocate old block. 
            # Otherwise, add the blockNumber to the end of the file.
            if nDeallocateIdx < len(inode.blk_numbers):
                interface.free_data_block( inode.blk_numbers[nDeallocateIdx] ) # deallocate old block
                nBlockNum = interface.get_valid_data_block() # allocate new block
                interface.update_data_block(nBlockNum, ''.join(nDataList)) # write to the new block
                inode.blk_numbers[nDeallocateIdx] = nBlockNum # replace file block numbers
            else:
                inode.blk_numbers.append(nBlockNum)

        # Output list either contains data from the indexed map's blocks -- or all NULL values
        # to represent a freshly initialized block.
        def NESTED_get_init_block_list(nBlockIdx):
            if inode.blk_numbers[nBlockIdx] > -1:
                return list(interface.BLOCK_NUMBER_TO_DATA_BLOCK(inode.blk_numbers[nBlockIdx]))
            else:
                return ['\0' for i in range(config.BLOCK_SIZE)]
       
        # _WRITE_TO_OFFSET BEGIN ----------------------------------------------
        
        # Locate the index of the block number in the inode.block_nums referenced by the input offset.
        iBlock = 0 # block index for the self.map list
        while offset >= config.BLOCK_SIZE:
            offset -= config.BLOCK_SIZE
            iBlock += 1

        # Read the current data stored at the block.
        blockList = NESTED_get_init_block_list(iBlock)

        # Do not allow the file to exceed the maximum file size the inode can handle.
        # 8 subtracted from the block numbers for the file name.
        if iBlock < len(inode.blk_numbers) - config.MAX_FILE_NAME_SIZE:
            
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

if __name__ == '__main__':
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE) # create the inode object of file type
    
    print "CREATION TIME: " + inode.time_created
    print "ACCESS TIME: " + inode.time_accessed
    print "MODIFY TIME: " + inode.time_modified
    print ""
    time.sleep(1)

    #InodeLay.write(inode, 0, "Test string") # write to the inode object
    #InodeLay.read(inode, 0, 5) # read back the entire string from the inode object
    
    # test between multiple blocks ("Hello " => block 8, "world" => block 9)
    InodeLay.write(inode, 506, "Hello world") # write to the inode object
    InodeLay.read(inode, 506, 11) # read back the entire string from the inode object

    print "CREATION TIME: " + inode.time_created
    print "ACCESS TIME: " + inode.time_accessed
    print "MODIFY TIME: " + inode.time_modified
   
    #InodeLay.status()

