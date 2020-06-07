'''
THIS MODULE PERFORMS HAS INODE STRUCTURE DEFINITIONS AND OPERATIONS REGARDING CONVERTING THE INODE STRUCTURE FROM TABLE TO ARRAY AND VICE VERSA.
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


#INODE STORED IN THE FORM OF ARRAY IN THE MEMORY DEPENDING UPON THE SIZE OF INODE GIVEN
class Array_Inode():
	def __init__(self, type):
		self.inode = [None for _ in range(8)]
		self.inode[0] = type  									#Type of inode => 2bytes
		self.inode[1] = ""    									#Name of the inode => 16bytes
		self.inode[2] = 2 if type == 1 else 1   			 	#Links of the inode => 2bytes
		self.inode[3] = ""    								 	#Time created => 19bytes
		self.inode[4] = ""   								 	#Time acessed => 19bytes
		self.inode[5] = ""    									#Time modified => 19bytes
		self.inode[6] = 0      									#Size of the inode(in case of file - filesize) => 2bytes
		if self.inode[0] == 0:
			max_data_blocks_allocated = (config.INODE_SIZE - 63 - config.MAX_FILE_NAME_SIZE) / 2  
			if max_data_blocks_allocated <= 0:
				print("CONFIG FILE ERROR")
				return -1   
			self.inode[7] = [-1 for _ in range(max_data_blocks_allocated)]
		else:
			entry_size = config.MAX_FILE_NAME_SIZE + len(str(config.MAX_NUM_INODES))
			max_entries = (config.INODE_SIZE - 63 - config.MAX_FILE_NAME_SIZE ) / entry_size
			if max_entries <= 0: 
				print("CONFIG FILE ERROR")
				return -1
			
			def new_entry():    #aLLOCATING MEMORY EACH TIME
				entry = ["\0" for _ in range(entry_size)]
				for i in range(entry_size):
					if i >= config.MAX_FILE_NAME_SIZE: entry[i] = "0"
				return entry
			
			self.inode[7] = [new_entry() for _ in range(max_entries)] 
 

#INCLUDE FUNCTIONS OF CONVERSION 
class InodeOperations():

	def convert_array_to_table(self, array_inode):
		if not array_inode: return False
		table_inode = Table_Inode(array_inode[0])
		table_inode.type = array_inode[0]
		table_inode.name = array_inode[1]
		table_inode.links = array_inode[2]
		table_inode.time_created = array_inode[3]
		table_inode.time_accessed = array_inode[4]
		table_inode.time_modified = array_inode[5]
		table_inode.size = array_inode[6]
		if array_inode[0] == 0: 
			for i in range(len(array_inode[7])): table_inode.blk_numbers[i] = array_inode[7][i]
		else:
			for i in range(len(array_inode[7])):
				string = "".join(array_inode[7][i])
				if string[0] == '\0': continue   #empty string
				inode_num_str = string[config.MAX_FILE_NAME_SIZE : ]
				filename = string[:config.MAX_FILE_NAME_SIZE].replace('\0', "")
				table_inode.directory[filename] = int(inode_num_str)
		return table_inode

	def convert_table_to_array(self, table_inode):
		if not table_inode: return False
		array = Array_Inode(table_inode.type)
		array.inode[0] = table_inode.type
		array.inode[1] = table_inode.name
		array.inode[2] = table_inode.links 
		array.inode[3] = table_inode.time_created
		array.inode[4] = table_inode.time_accessed
		array.inode[5] = table_inode.time_modified
		array.inode[6] = table_inode.size 
		if table_inode.type == 0:
			for i in range(len(table_inode.blk_numbers)):
				array.inode[7][i] = table_inode.blk_numbers[i]
		else:
			if len(table_inode.directory): 
				num = 0
				for x in table_inode.directory:
					for i in range(len(x)): array.inode[7][num][i] = x[i]	
					integar_length = len(str(config.MAX_NUM_INODES))
					number_string = '{:0>{}}'.format(str(table_inode.directory[x]), integar_length)			#PADDING \0 AT THE LAST
					for i in range(len(number_string)): array.inode[7][num][i + config.MAX_FILE_NAME_SIZE] = number_string[i]
					num += 1
		return array.inode