'''
THIS MODULE CONSISTS OF DEFINITIONS OF SUPERBLOCK AND ITS ATTRIBUTES. IT ALSO INCLUDES DEFINITIONS OF BITMAP BLOCKS, INODE BLOCKS
AND DATA BLOCKS
'''
import config

class SuperBlock():
    def __init__(self):
        self.TOTAL_NO_OF_BLOCKS = config.TOTAL_NO_OF_BLOCKS                     #DECIDED BY CONFIG FILE
        self.BLOCK_SIZE = config.BLOCK_SIZE                                     #DECIDED BY CONFIG FILE
        self.MAX_NUM_INODES = config.MAX_NUM_INODES                             #DECIDED BY CONFIG FILE
        self.INODE_SIZE = config.INODE_SIZE                                     #DECIDED BY CONFIG FILE
        self.INODES_PER_BLOCK = config.BLOCK_SIZE / config.INODE_SIZE           #CALCULATED 
        self.ADDR_BITMAP_BLOCKS = []                                            #POINTER TO BITMAP BLOCKS
        self.ADDR_INODE_BLOCKS = []                                             #POINTER TO INODE BLOCK
        self.ADDR_DATA_BLOCKS = []                                              #POINTER TO DATA BLOCKS
        self.DATA_BLOCKS_OFFSET = -1                                            #INITIALLY BEFORE FILE SYSTEM INITIALIZATION ALL OFFSETS ARE -1
        self.INODE_BLOCKS_OFFSET = -1                                           #THESE OFFSETS WILL BE DEPENDENT UPON, THE PARAMETERS GIVEN IN CONFIG FILE                                     
        self.BITMAP_BLOCKS_OFFSET = -1

class Bitmap_Block():
    def __init__(self, BLOCK_SIZE):
        self.block = [0]*BLOCK_SIZE

class Inode_Block():
    def __init__(self, INODES_PER_BLOCK):
        self.block = [False]* INODES_PER_BLOCK

class Data_Block():
    def __init__(self, BLOCK_SIZE):                                 
        self.block = ["\0"]*BLOCK_SIZE                                          #EMPTY BLOCK WILL CONTAIN NULL VALUES INITIALLY