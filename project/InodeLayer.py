'''
THIS MODULE IS INODE LAYER OF THE FILE SYSTEM. IT INCLUDES THE INODE DEFINITION DECLARATION AND GLOBAL HANDLE OF BLOCK LAYER OF API.
THIS MODULE IS RESPONSIBLE FOR PROVIDING ACTUAL BLOCK NUMBERS SAVED IN INODE ARRAY OF BLOCK NUMBERS TO FETCH DATA FROM BLOCK LAYER.
'''
import datetime, config, BlockLayer, InodeOps, MemoryInterface, math

INODETYPE_FILE  = 0
INODETYPE_DIR   = 1
INODETYPE_SYM   = 2

#HANDLE OF BLOCK LAYER
interface = BlockLayer.BlockLayer()

class InodeLayer():

    #RETURNS BLOCK NUMBER FROM RESPECTIVE INODE DIRECTORY
    def INDEX_TO_BLOCK_NUMBER(self, inode, index):
        if index == len(inode.blk_numbers): return -1
        return inode.blk_numbers[index]


    #RETURNS BLOCK DATA FROM INODE
    def INODE_TO_BLOCK(self, inode, offset):
        index = offset / config.BLOCK_SIZE
        block_number = self.INDEX_TO_BLOCK_NUMBER(inode, index)
        if block_number == -1: return ''
        else: return interface.BLOCK_NUMBER_TO_DATA_BLOCK(block_number)


    #MAKES NEW INODE OBJECT
    def new_inode(self, type):
        return InodeOps.Table_Inode(type)


    #FLUSHES ALL THE BLOCKS OF INODES FROM GIVEN INDEX OF MAPPING ARRAY  
    def free_data_block(self, inode, index):
        for i in range(index, len(inode.blk_numbers)):
	    if(inode.blk_numbers[i] != -1):
            	interface.free_data_block(inode.blk_numbers[i])
            	inode.blk_numbers[i] = -1


    '''
    SUMMARY: write
    This function writes characters of a string to blocks pointed at 
    by the inode.blk_numbers.
    '''
    def write(self, inode, offset, data):
        
        # return an error if the input inode is not a file type.
        if inode.type != INODETYPE_FILE: return -1
        
        # file size error handler
        if offset > inode.size or offset < 0: return -1
        
        inode.time_accessed = str(datetime.datetime.now())[:19] # change time accessed

        blockOffset = offset / config.BLOCK_SIZE
        
        # make sure the inode is not a directory before writing to the blocks.
        if blockOffset < len(inode.blk_numbers):
            # If file is a block, overwrite data beginning at the offset.
            self.__write_to_offset(inode, offset, data)
            inode.time_modified = str(datetime.datetime.now())[:19] # change time modified
            return inode # updated inode
            
        else: 
            return -1 # attempting to write to a directory

    '''
    SUMMARY: read
    This function reads up to "length" bytes starting form the offset
    from blocks indexed by the inode objects.
    '''
    def read(self, inode, offset, length):
        
        # return an error if the input inode is not a file type.
        if inode.type != INODETYPE_FILE: return -1
        
        # file size error handler
        if offset > inode.size or offset < 0: return -1
        
        # find the offset's block number
        blockOffset = offset / config.BLOCK_SIZE
        offset = offset % config.BLOCK_SIZE
        
        # go through all blocks until number of requested bytes are read.
        data = []
        for i in range(blockOffset, len(inode.blk_numbers)):
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
        
        # change time accessed
        inode.time_accessed = str(datetime.datetime.now())[:19]
        return (inode, "".join(data)) # returns a tuple of read data and the updated inode
    
    '''
    SUMMARY: copy
    Deep copy the contents of the passed inode to a new inode.
    '''
    def copy(self, inode):
        
        # return an error if the input inode is not a file type.
        if inode.type != INODETYPE_FILE: return -1
        
        newInode = self.new_inode(INODETYPE_FILE)
        self.free_data_block(newInode, 0) # clear all data located in the new inode
        
        # for all valid blocks in the original inode, get a valid data block,
        # copy the contents of the original block into the newly acquired block,
        # and assign the block number to the newInode's blk_numbers.
        for i in range(0, len(inode.blk_numbers)):
            origBlockNum = inode.blk_numbers[i]
            if origBlockNum == -1:
                continue # do not attempt to copy the contents of invalid block numbers
            else:
                
                # copy the contents of the block into the new block and assign the 
                # block to the newInode blk_numbers map.
                newBlockNum = interface.get_valid_data_block()
                #dataToCopy = interface.BLOCK_NUMBER_TO_DATA_BLOCK(origBlockNum) # read contents from the original block num
                #interface.update_data_block(newBlockNum, dataToCopy) # write the contents to a new block number
                newInode.blk_numbers[i] = newBlockNum
                
                inode, dataToCopy = self.read(inode, i*config.BLOCK_SIZE, config.BLOCK_SIZE) # read original contents/modify time
                self.write(newInode, i*config.BLOCK_SIZE, dataToCopy) # write to copy/modify time
                
        return newInode

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
                if(inode.blk_numbers[nDeallocateIdx] != -1): 
                    interface.free_data_block( inode.blk_numbers[nDeallocateIdx] ) # deallocate old block
                nBlockNum = interface.get_valid_data_block() # allocate new block
                interface.update_data_block(nBlockNum, ''.join(nDataList)) # write to the new block
                inode.blk_numbers[nDeallocateIdx] = nBlockNum # replace file block numbers
            else:
                inode.blk_numbers.append(nBlockNum)

        # Output list either contains data from the indexed map's blocks -- or all NULL values
        # to represent a freshly initialized block.
        def NESTED_get_init_block_list(nBlockIdx):
            # if the block index is out of range, return an error.
            if nBlockIdx >= len(inode.blk_numbers): return -1
            
            # find a block to write data to.
            if inode.blk_numbers[nBlockIdx] > -1:
                return list(interface.BLOCK_NUMBER_TO_DATA_BLOCK(inode.blk_numbers[nBlockIdx]))
            else:
                return ['\0' for i in range(config.BLOCK_SIZE)]
       
        # _WRITE_TO_OFFSET BEGIN ----------------------------------------------
        self.free_data_block(inode, (int)(math.floor(offset/config.BLOCK_SIZE)))
        inode.size = offset
        
        # Locate the index of the block number in the inode.block_nums referenced by the input offset.
        iBlock = 0 # block index for the self.map list
        while offset >= config.BLOCK_SIZE:
            offset -= config.BLOCK_SIZE
            iBlock += 1
            
        # Read the current data stored at the block.
        blockList = NESTED_get_init_block_list(iBlock)

        # Do not allow the file to exceed the maximum file size the inode can handle.
        if iBlock < len(inode.blk_numbers):
            
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
                    if blockList == -1: return -1 # stop writing if in the last block.

                # Replace the next offset value with the string contents.
                blockList[offset] = string[charCnt]
                offset += 1 # next index for the block
                charCnt += 1 # next index for the new string
                inode.size += 1 # size of inode matches number of bytes in the file
            
            # if the block contains data longer than the input string, remove the extra characters
            if offset < config.BLOCK_SIZE: 
                blockList[offset:] = '\0'
            NESTED_write_filesystem_map(iBlock, blockList)
            return 0

        else:
            return -1   
