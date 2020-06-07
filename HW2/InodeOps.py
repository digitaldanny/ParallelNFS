'''
THIS MODULE PERFORMS HAS INODE STRUCTURE DEFINITIONS.
'''

import datetime, config


#TABLE INODE STRUCTURE FOR LOCAL USE OF OPERATIONS
class Table_Inode():
	def __init__(self, type):
		self.type = type  													
		self.blk_numbers = [-1 for _ in range(((config.INODE_SIZE - 63 - config.MAX_FILE_NAME_SIZE) / 2))]   
		self.directory = dict()
		self.time_created = str(datetime.datetime.now())[:19]
		self.time_accessed = str(datetime.datetime.now())[:19]
		self.time_modified = str(datetime.datetime.now())[:19]
		self.size = 0 if self.type == 0 else len(self.directory)
		self.links = 2 if self.type == 1 else 1
		self.name = ""

#self.type = type  													
#self.blk_numbers - same as (self.map in HW1) mapping table between actual block numbers in memory vs relative block numbers 
#self.directory - for storing directory inodes
#self.links - for Links
#63 = (19bytes)time accessed + (19bytes)time created + (19bytes)time modified  + (2 bytes)InodeType + (2 bytes)Size of file
