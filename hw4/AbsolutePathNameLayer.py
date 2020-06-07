'''
THIS MODULE SERVE AS A TOP MOST MODULE OF FILE SYSTEM LAYER. IT CONNECTS THE FILE SYSTEM OPERATIONS WITH FILE SYSTEM LAYERS. 
IT ALSO PROVIDES ABSOLUTE PATH RESPECTIVE TO ROOT DIRECTORY. IT TAKES COMPLETE PATH AS THE INPUT.
'''

import FileNameLayer


#HANDLE OF FILE NAME LAYER
interface = FileNameLayer.FileNameLayer()

class AbsolutePathNameLayer():

	#RETURNS INODE NUMBER OF HOME DIRECTORY IF CORRECT PATH IS GIVEN
	def GENERAL_PATH_TO_HOME_INODE_NUMBER(self, path):
		path_array = path.split('/')
		if len(path_array) > 1 and path_array[0] == '': return 0
		else: return -1

	
	#MAKES NEW
	def new_entry(self, path, type):
		if path == '/':   #SPECIAL CASE OF INITIALIZING FILE SYSTEM
			interface.new_entry('/', -1, type)
			return 
		inode_number_of_parent = self.GENERAL_PATH_TO_HOME_INODE_NUMBER(path)
		if inode_number_of_parent == -1: 
			print("Error AbsolutePathLayer: Wrong Path!")
			return -1
		interface.new_entry(path[1:], inode_number_of_parent, type)


	#IMPLEMENTS READ 
	def read(self, path, offset, length):
		inode_number_of_parent = self.GENERAL_PATH_TO_HOME_INODE_NUMBER(path)
		if inode_number_of_parent == -1: 
			print("Error AbsolutePathLayer: Wrong Path Given!\n")
			return -1
		return interface.read(path[1:], inode_number_of_parent, offset, length)


	#IMPLEMENTS WRITE
	def write(self, path, offset, data):
		inode_number_of_parent = self.GENERAL_PATH_TO_HOME_INODE_NUMBER(path)
		if inode_number_of_parent == -1: 
			print("Error AbsolutePathLayer: Wrong Path Given!\n")
			return -1
		interface.write(path[1:], inode_number_of_parent, offset, data)


	#IMPLEMENTS THE HARDLINK
	def link(self, old_path, new_path):
		inode_number_of_parent = self.GENERAL_PATH_TO_HOME_INODE_NUMBER(old_path)
		if inode_number_of_parent == -1: 
			print("Error AbsolutePathLayer: Wrong Path Given!\n")
			return -1
		interface.link(old_path[1:], new_path[1:], inode_number_of_parent)


	#IMPLEMENTS DELETE
	def unlink(self, path):
		inode_number_of_parent = self.GENERAL_PATH_TO_HOME_INODE_NUMBER(path)
		if inode_number_of_parent == -1: 
			print("Error AbsolutePathLayer: Wrong Path Given!\n")
			return -1
		interface.unlink(path[1:], inode_number_of_parent)
	

	#MOVE
	def mv(self, old_path, new_path):
		inode_number_of_parent = self.GENERAL_PATH_TO_HOME_INODE_NUMBER(old_path)
		if inode_number_of_parent == -1: 
			print("Error AbsolutePathLayer: Wrong Path Given!\n")
			return -1
		interface.mv(old_path[1:], new_path[1:], inode_number_of_parent)