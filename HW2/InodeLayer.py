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
        inode.time_accessed = str(datetime.datetime.now())[:19] # change time accessed
        
        blockOffset = offset / config.BLOCK_SIZE
        
        # make sure the inode is not a directory before writing to the blocks.
        if inode.type == config.INODETYPE_FILE and blockOffset < len(inode.blk_numbers):
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
        if inode.type != config.INODETYPE_FILE: return -1
        
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
        if inode.type != config.INODETYPE_FILE: return -1
        
        newInode = self.new_inode(config.INODETYPE_FILE)
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
                
                inode, dataToCopy = self.read(inode, i*512, 512) # read original contents/modify time
                self.write(newInode, i*512, dataToCopy) # write to copy/modify time
                
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
            
            NESTED_write_filesystem_map(iBlock, blockList)
            return 0

        else:
            return -1   

'''
SUMMARY: test00_createAccessModifyTime
The purpose of this script is to test whether the write and read functions 
correctly modify the time_created, time_accessed, and time_modified parameters.
'''
def test00_createAccessModifyTime():
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE) # create the inode object of file type
    
    print "TIME BEFORE WRITE"
    print "CREATION TIME: " + inode.time_created
    print "ACCESS TIME: " + inode.time_accessed
    print "MODIFY TIME: " + inode.time_modified
    print ""

    #InodeLay.write(inode, 0, "Test string") # write to the inode object
    #InodeLay.read(inode, 0, 5) # read back the entire string from the inode object
    
    # test between multiple blocks ("Hello " => block 8, "world" => block 9)
    time.sleep(1)
    InodeLay.write(inode, 506, "Hello world") # write to the inode object
    print "TIME AFTER WRITE / BEFORE READ"
    print "CREATION TIME: " + inode.time_created
    print "ACCESS TIME: " + inode.time_accessed
    print "MODIFY TIME: " + inode.time_modified
    print ""
    
    time.sleep(1)
    InodeLay.read(inode, 506, 11) # read back the entire string from the inode object
    print "TIME AFTER READ"
    print "CREATION TIME: " + inode.time_created
    print "ACCESS TIME: " + inode.time_accessed
    print "MODIFY TIME: " + inode.time_modified
    print ""

    InodeLay.free_data_block(inode, 0) # reset the memory before goinig to the next test
    return 0

'''
SUMMARY: test01_rwTwoBlocks
The purpose of this script is to test whether the InodeLayer can write a string
over more than 1 block of data and read back the same data.
'''
def test01_rwTwoBlocks():
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE) # create the inode object of file type
    inputString  = "Hello world"
    
    # test between multiple blocks ("Hello " => block 8, "world" => block 9)
    InodeLay.write(inode, 506, inputString) # write to the inode object
    (inode, mess) = InodeLay.read(inode, 506, 11) # read back the entire string from the inode object
    InodeLay.status()
    
    if mess == inputString:
        InodeLay.free_data_block(inode, 0) # reset the memory before goinig to the next test
        return 0
    else:
        return -1
  
'''
SUMMARY: test02_deepCopy
The purpose of this script is to test whether the copy function will copy all
the file contents of the original inode into a new inode with different block
numbers.
'''
def test02_deepCopy():
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE)
    
    # load data into the first inode
    messages = []
    for i in range(0, 4):
        messages.append("Test string for block " + str(i))
        InodeLay.write(inode, i*512, messages[i])
    
    # copy the data from the original inode into the new inode
    print "Memory blocks BEFORE copy."
    InodeLay.status() # memory blocks before copy
    newInode = InodeLay.copy(inode)
    print "Memory blocks AFTER copy."
    InodeLay.status() # memory blocks after copy
    
    # check if the contents of the new inode are equal to the loaded data in
    # the original inode
    for i in range(0,4):
        (newInode, readData) = InodeLay.read(newInode, i*512, len(messages[i]))
        if readData != messages[i]:
            print "ORIGINAL: " + messages[i]
            print "COPIED: " + readData
            return -1
    
    InodeLay.free_data_block(inode, 0) # reset the memory before goinig to the next test
    InodeLay.free_data_block(newInode, 0) # reset the memory before goinig to the next test
    return 0

'''
SUMMARY: This test confirms requirement 1: Your design must return an error if
the inode type is not a file.
'''
def test03_dirTest():
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_DIR)
    
    # try writing to the directory 
    inode = InodeLay.write(inode, 0, "This write should fail")
    InodeLay.status()
    
    if inode == -1:
        print "Could not write to directory"
        return 0
    else:
        print "ERROR: Wrote to a directory"
        return -1
    
'''
SUMMARY: This function tests that the InodeLayer will not allow writes when 
the initial offset is at a block greater than the maximum INODE_SIZE.
'''
def test04_fileSizeError():
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE)
    
    # try writing too much data to the file
    inode = InodeLay.write(inode, 512*len(inode.blk_numbers) + 10, "None of this string should be written")
    InodeLay.status()

    if inode == -1:
        print "No data was written"
        return 0
    else:
        print "ERROR: Data was written"
        return -1
    
'''
SUMMARY: Tests that data can be written to the last block before INODE_SIZE before
being truncated when attempting to overflow to the next block.
'''
def test05_trucateFileSize():
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE)
    
    # try writing too much data to the file
    inode = InodeLay.write(inode, 512*len(inode.blk_numbers) - 10, "Only some of this string should stay")
    InodeLay.status()

    inode, data = InodeLay.read(inode, 512*len(inode.blk_numbers) - 10, 10) # read all the data possible
    
    if data == "Only some ":
        InodeLay.free_data_block(inode, 0) # reset the memory before goinig to the next test
        print "Data was successfuly truncated"
        return 0
    else:
        print "Data was NOT truncated"
        return -1
    
'''
SUMMARY: Tests that a very large string can be written to all blocks AND truncate
at the end.
'''
def test06_allBlockRW():
    InodeLay = InodeLayer()
    inode = InodeLay.new_inode(config.INODETYPE_FILE)
    
    message = "a" * 512 * (len(inode.blk_numbers) + 1)
    InodeLay.write(inode, 0, message)
    
    #inode, data = InodeLay.read(inode, 0, )
    InodeLay.status()
    InodeLay.free_data_block(inode, 0) # reset the memory before goinig to the next test
    return 0

if __name__ == '__main__':

    # names of all tests being run
    testbenches = [
         test06_allBlockRW,
         test00_createAccessModifyTime,
         test01_rwTwoBlocks,
         test02_deepCopy,
         test03_dirTest,
         test04_fileSizeError,
         test05_trucateFileSize
    ]
    
    messages = []
    
    # run all tests and mark when it passed or failled
    for test in testbenches:
        print "\n****************** RUNNING NEXT TEST ******************\n"
        passed = test()
        message = test.__name__ + ": "
        if passed == 0:
            message += "OK"
        else:
            message += "failed"
        messages.append(message)
        
    # after all tests have been run, output the results.
    print "\n+-----+-----+-----+-----+-----+-----+-----+-----+"
    for message in messages: print message
    print "+-----+-----+-----+-----+-----+-----+-----+-----+\n"
