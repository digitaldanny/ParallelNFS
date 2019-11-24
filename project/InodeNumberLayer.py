'''
THIS MODULE ACTS AS A INODE NUMBER LAYER. NOT ONLY IT SHARES DATA WITH INODE LAYER, BUT ALSO IT CONNECTS WITH MEMORY INTERFACE FOR INODE TABLE 
UPDATES. THE INODE TABLE AND INODE NUMBER IS UPDATED IN THE FILE SYSTEM USING THIS LAYER
'''
import InodeLayer, config, MemoryInterface, datetime, InodeOps


#HANDLE OF INODE LAYER
interface = InodeLayer.InodeLayer()

class InodeNumberLayer():

    #PLEASE DO NOT MODIFY
    #ASKS FOR INODE FROM INODE NUMBER FROM MemoryInterface.(BLOCK LAYER HAS NOTHING TO DO WITH INODES SO SEPERTAE HANDLE)
    def INODE_NUMBER_TO_INODE(self, inode_number):
        array_inode = MemoryInterface.inode_number_to_inode(inode_number)
	#print("INTI: array_inode", array_inode)
        inode = InodeOps.InodeOperations().convert_array_to_table(array_inode)
	#print(inode)
        if inode: inode.time_accessed = datetime.datetime.now()   #TIME OF ACCESS
        return inode


    #PLEASE DO NOT MODIFY
    #RETURNS DATA BLOCK FROM INODE NUMBER
    def INODE_NUMBER_TO_BLOCK(self, inode_number, offset, length):
        inode = self.INODE_NUMBER_TO_INODE(inode_number)
        if not inode:
            print("Error InodeNumberLayer: Wrong Inode Number! \n")
            return -1
        return interface.read(inode, offset, length)


    #PLEASE DO NOT MODIFY
    #UPDATES THE INODE TO THE INODE TABLE
    def update_inode_table(self, table_inode, inode_number):
        if table_inode: table_inode.time_modified = datetime.datetime.now()  #TIME OF MODIFICATION 
        array_inode = InodeOps.InodeOperations().convert_table_to_array(table_inode)
        MemoryInterface.update_inode_table(array_inode, inode_number)


    #PLEASE DO NOT MODIFY
    #FINDS NEW INODE INODE NUMBER FROM FILESYSTEM
    def new_inode_number(self, type, parent_inode_number, name):
        if parent_inode_number != -1:
            parent_inode = self.INODE_NUMBER_TO_INODE(parent_inode_number)
            if not parent_inode:
                print("Error InodeNumberLayer: Incorrect Parent Inode")
                return -1
            entry_size = config.MAX_FILE_NAME_SIZE + len(str(config.MAX_NUM_INODES))
            max_entries = (config.INODE_SIZE - 79 ) / entry_size
            if len(parent_inode.directory) == max_entries:
                print("Error InodeNumberLayer: Maximum inodes allowed per directory reached!")
                return -1
        for i in range(0, config.MAX_NUM_INODES):
            if self.INODE_NUMBER_TO_INODE(i) == False: #FALSE INDICTES UNOCCUPIED INODE ENTRY HENCE, FREEUMBER
                inode = interface.new_inode(type)
                inode.name = name
                self.update_inode_table(inode, i)
                return i
        print("Error InodeNumberLayer: All inode Numbers are occupied!\n")

    '''
    SUMMARY: link
    This function creates a hard link from hardlink_parent/hardlink_name to 
    the file's inode number and increments the filename_inode's reference count.
    
    PARENT INODE (inode 1)                           FILE INODE (inode 2)
    +-----------+-----------------+                  +--------+-----+
    | link_name |  file_inode_num |                  |    blk_nums  |
    | 'f'       |       2         | ---------------> | 10, 11, 12   |
    |           |                 |                  |              |
    |           |                 |                  |              |
    +-----------------------------+                  +--------------+ 
    |          type = dir         |                  | type = file  |
    +-----------------------------+                  +--------------+
    '''
    def link(self, file_inode_number, hardlink_name, hardlink_parent_inode_number): 
        
        # get the parent inode - if inode does not exist, return an error.
        dirInode = self.INODE_NUMBER_TO_INODE(hardlink_parent_inode_number)
        if dirInode == -1: return -1
        
        # get the file inode to link to
        targetInode = self.INODE_NUMBER_TO_INODE(file_inode_number)
        if targetInode == -1: return -1
        
        # directory types cannot have hard links
        if targetInode.type == InodeLayer.INODETYPE_DIR: return -1
        
        # add the directory parameters to link from directory to inode
        dirInode.directory[hardlink_name] = file_inode_number 
        targetInode.links += 1 # new directory is referencing the inode
        
        self.update_inode_table(targetInode, file_inode_number) # update the target file/directory
        self.update_inode_table(dirInode, hardlink_parent_inode_number) # update the parent directory
        return True

    '''
    SUMMARY: unlink
    This function removes a link in the file system for an inode number.
    If the last link is removed from the inode number, all blocks in the blk_numbers
    are deallocated + the inode is freed.
    '''
    def unlink(self, inode_number, parent_inode_number, filename):
        
        # get the parent inode - if inode does not exist, return an error.
        dirInode = self.INODE_NUMBER_TO_INODE(parent_inode_number)
        if dirInode == -1: return -1
        
        # if the {filename, inode}'s inode does not match the inode_number 
        # passed in, the function should return an error.
        if inode_number != dirInode.directory[filename]: return -1
        targetInode = self.INODE_NUMBER_TO_INODE(inode_number)
        if targetInode == -1: return -1
        
        # unlinking file OR directory
        if targetInode.type == InodeLayer.INODETYPE_DIR:
            
            # if a directory is being unlinked, make sure that it is empty first
            # eg. directory.links == 2. The link can only be decremented by unlinking
            # all of the file inside the directory first.
            # ---------------------------------------------------------------------
            #if targetInode.links == 2:
            if len(targetInode.directory.values()) == 0:
                
                # handle changes to the parent inode first
                del dirInode.directory[filename] # delete the mapping of the {filename, inode}
                #dirInode.links -= 1 # one of the directories inside is being removed.
                
                # deallocate the target directory inode
                self.__deallocate_inode_number(inode_number) # deletes target inode and empties spot in array
                self.update_inode_table(dirInode, parent_inode_number) # update the parent directory
        
            else:
                print "ERROR: No changes to the path. Directory still contains files."
                return -1
        else:
            
            # handle changes to the parent inode first
            del dirInode.directory[filename] # delete the mapping of the {filename, inode}
            #dirInode.links -= 1 # one of the directories inside is being removed.
            
            # if a file is being unlinked, decrement the link count of the inode
            # that it is mapped to.
            # ---------------------------------------------------------------------
            targetInode.links -= 1
        
            # if the inode's reference count == 0, remove all the contents of the 
            # inode and reinitialize the blocks pionted at by the blk_numbers.
            if targetInode.links == 0:
                self.__deallocate_inode_number(inode_number) # deletes target inode and empties spot in array
                self.update_inode_table(dirInode, parent_inode_number) # update the parent directory
                return True
            
        self.update_inode_table(targetInode, inode_number) # update the target file/directory
        self.update_inode_table(dirInode, parent_inode_number) # update the parent directory
        return True

    '''
    SUMMARY: write
    This function uses the InodeLayer write function to write data to an inode's
    block numbers in a specific directory.
    
    Ex. parent_inode_number/inode_number offset = 10, data = "Hello world"
    '''
    def write(self, inode_number, offset, data, parent_inode_number):
        
        # get the parent inode - if inode does not exist, return an error.
        dirInode = self.INODE_NUMBER_TO_INODE(parent_inode_number)
        if dirInode == -1: return -1
        
        # search for the file inode inside the parent (directory) inode as a 
        # value of the {filename, inode} dictionary.
        if inode_number not in dirInode.directory.values(): return -1
        fileInode = self.INODE_NUMBER_TO_INODE(inode_number)
        
        # write data to the file inode using the InodeLayer.write
        fileInode = interface.write(fileInode, offset, data)
        if fileInode == -1: return -1
        
        # update the inodeArray with the new file inode
        self.update_inode_table(fileInode, inode_number)
        return True
		

    '''
    SUMMARY: read
    This function uses the InodeLayer read function to read data to an inode's
    block numbers in a specific directory. This function gets inode's from 
    the inodeArray from the input inodeNumbers.
    '''
    def read(self, inode_number, offset, length, parent_inode_number):
        
        # get the parent inode - if inode does not exist, return an error.
        dirInode = self.INODE_NUMBER_TO_INODE(parent_inode_number)
	#print("dirInode",dirInode)
        if dirInode == -1: return -1
        
        # search for the file inode inside the parent (directory) inode as a 
        # value of the {filename, inode} dictionary.
	#print("DIRINIDE",dirInode.directory.values(),inode_number)
        if inode_number not in dirInode.directory.values(): return -1
        fileInode = self.INODE_NUMBER_TO_INODE(inode_number)
        
        # write data to the file inode using the InodeLayer.write
        (fileInode, dataBuffer) = interface.read(fileInode, offset, length)
        return dataBuffer
    
    '''
    This function deallocates all blocks in the inode of the inode number passed
    to it. The function also deallocates the inode itself.
    '''
    def __deallocate_inode_number(self, inode_number):
        inode = self.INODE_NUMBER_TO_INODE(inode_number)
        
        # deallocate valid block numbers in InodeLayer pointed at by the inode.blk_numbers
        interface.free_data_block(inode, 0)
        del inode
        
        # deallocate the inode also and push FALSE back to the inode array
        # so the inode number can be used in new_inode_number()
        #del inode
        self.update_inode_table(False, inode_number)
        
