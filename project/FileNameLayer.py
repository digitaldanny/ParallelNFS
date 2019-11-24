'''
THIS MODULE ACTS LIKE FILE NAME LAYER AND PATH NAME LAYER (BOTH) ABOVE INODE LAYER.
IT RECIEVES INPUT AS PATH (WITHOUT INITIAL '/'). THE LAYER IMPLEMENTS LOOKUP TO FIND INODE NUMBER OF THE REQUIRED DIRECTORY.
PARENTS INODE NUMBER IS FIRST EXTRACTED BY LOOKUP AND THEN CHILD INODE NUMBER BY RESPECTED FUNCTION AND BOTH OF THEM ARE UPDATED
'''
import InodeNumberLayer

#HANDLE OF INODE NUMBER LAYER
interface = InodeNumberLayer.InodeNumberLayer()

class FileNameLayer():

    #PLEASE DO NOT MODIFY
    #RETURNS THE CHILD INODE NUMBER FROM THE PARENTS INODE NUMBER
    def CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(self, childname, inode_number_of_parent):
        inode = interface.INODE_NUMBER_TO_INODE(inode_number_of_parent)
        if not inode: 
            print("Error FileNameLayer: Lookup Failure!")
            return -1
        if inode.type == 0:
            print("Error FileNameLayer: Invalid Directory!")
            return -1
        if childname in inode.directory: return inode.directory[childname]
        print("Error FileNameLayer: Lookup Failure-notinparent!")
        return -1

    #PLEASE DO NOT MODIFY
    #RETUNS THE PARENT INODE NUMBER FROM THE PATH GIVEN FOR A FILE/DIRECTORY 
    def LOOKUP(self, path, inode_number_cwd):   
        name_array = path.split('/')
        if len(name_array) == 1: return inode_number_cwd
        else:
            child_inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(name_array[0], inode_number_cwd)
            if child_inode_number == -1: return -1
            return self.LOOKUP("/".join(name_array[1:]), child_inode_number)

    #PLEASE DO NOT MODIFY
    #MAKES NEW ENTRY OF INODE
    def new_entry(self, path, inode_number_cwd, type):
        if path == '/': #SPECIAL CASE OF INITIALIZING FILE SYSTEM
            interface.new_inode_number(type, inode_number_cwd, "root")
            return True
        parent_inode_number = self.LOOKUP(path, inode_number_cwd)
	#fails when parent inode number is -1. Meaning Lookup Failed
        parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number) 
        childname = path.split('/')[-1]
        if not parent_inode: return -1
        if childname in parent_inode.directory:
            print("Error FileNameLayer: File already exists!")
            return -1
        child_inode_number = interface.new_inode_number(type, parent_inode_number, childname)  #make new child
        if child_inode_number != -1:
            parent_inode.directory[childname] = child_inode_number
            interface.update_inode_table(parent_inode, parent_inode_number)

    '''
    SUMMARY: read
    This function searches for the directory/file inode numbers, then passes
    those inode numbers down to the InodeNumberLayer.read function.
    '''
    def read(self, path, inode_number_cwd, offset, length):

        # search for the file/directory inode numbers to perform the read
        (parentInodeNum, childInodeNum) = self.__decode_parent_child_inode_nums(path, inode_number_cwd)
        if (parentInodeNum, childInodeNum) == (-1, -1): return -1

        # if the parent/child inode numbers have been found, read the data from the 
        # offset.
        return interface.read(childInodeNum, offset, length, parentInodeNum)
    
    '''
    SUMMARY: write
    This function searches for the directory/file inode numbers, then passes
    those inode numbers down to the InodeNumberLayer.write function.
    '''
    def write(self, path, inode_number_cwd, offset, data):
        
        # search for the file/directory inode numbers to perform the write
        (parentInodeNum, childInodeNum) = self.__decode_parent_child_inode_nums(path, inode_number_cwd)
        if (parentInodeNum, childInodeNum) == (-1, -1): return -1
        
        # if the parent/child inode numbers have been found, write the data to the 
        # offset.
        return interface.write(childInodeNum, offset, data, parentInodeNum)


    '''
    SUMMARY: link
    This function creates a hard link to the old_path's core file inode from the new_path's
    directory inode.
    '''
    def link(self, old_path, new_path, inode_number_cwd):
        
        # get the inode number for the old_path's core file.
        (unusedParentInodeNum, childInodeNum) = self.__decode_parent_child_inode_nums(old_path, inode_number_cwd)
        if (unusedParentInodeNum, childInodeNum) == (-1, -1): return -1
    
        # get the filename to map to the new_path's parent
        pathComponents = new_path.split('/') # last value of the path is the file name
        childName = pathComponents[-1]
        
        # get the inode number for the new_path's parent directory.
        parentInodeNum = self.LOOKUP(new_path, inode_number_cwd) 
        if parentInodeNum == -1: -1
        
        return interface.link(childInodeNum, childName, parentInodeNum)


    '''
    SUMMARY: unlink
    This function decrements the inode's reference count. Additionally, if the
    reference count becomes equal to 0, the inode's blk_number contents are 
    deallocated and the inode is reset.
    '''
    def unlink(self, path, inode_number_cwd):
        if path == "": 
            print("Error FileNameLayer: Cannot delete root directory!")
            return -1
        
        # search for the file/directory inode numbers to perform the write
        (parentInodeNum, childInodeNum) = self.__decode_parent_child_inode_nums(path, inode_number_cwd)
        if (parentInodeNum, childInodeNum) == (-1, -1): return -1
        
        # get the filename to delete the mapping
        pathComponents = path.split('/') # last value of the path is the file name
        fileName = pathComponents[-1]
        
        return interface.unlink(childInodeNum, parentInodeNum, fileName)


    '''
    SUMMARY: mv
    This function moves directory paths AND renames the file.
    '''
    def mv(self, old_path, new_path, inode_number_cwd):
        err = self.link(old_path, new_path, inode_number_cwd)
        if err == -1: return -1
        
        err = self.unlink(old_path, inode_number_cwd)
        return err


    '''
    SUMMARY: __decode_parent_child_inode_nums
        This function performs the LOOKUPs required to find the final parent and 
        child inode numbers. 
    
    RETURNS: 
        ~ (-1, -1): either the parent inode number or child inode number does not exist
        ~ (parentInodeNum, childInodeNum): expected output
    '''
    def __decode_parent_child_inode_nums(self, path, inode_number_cwd):
        
        # search for the directory and file inode numbers for the write
        parentInodeNum = self.LOOKUP(path, inode_number_cwd) 
        if parentInodeNum == -1: return (-1,-1)
    
        pathComponents = path.split('/') # last value of the path is the file name
        childName = pathComponents[-1]
        
        childInodeNum = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(childName, parentInodeNum)
        if childInodeNum  == -1: return (-1,-1)   
        
        return (parentInodeNum, childInodeNum)
