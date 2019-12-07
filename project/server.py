# POCSD Final Project
# Server Stub 00

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import time, Memory, pickle , InodeOps, config, DiskLayout, sys, os

global portNumber

filesystem = Memory.Operations()

state = True
Quit = 0

def configure():
	configuration = [config.TOTAL_NO_OF_BLOCKS, config.BLOCK_SIZE, config.MAX_NUM_INODES, config.INODE_SIZE, config.MAX_FILE_NAME_SIZE]
	retVal        = pickle.dumps((configuration, state))
	return retVal

def Initialize():
        print('+-----'*10)
        print('Initialize')
        print('+-----'*10)
	retVal = Memory.Initialize()
	retVal = pickle.dumps((retVal,state))
	return retVal

def addr_inode_table():
        print('+-----'*10)
        print('addr_inode_table')
        print('+-----'*10)
	retVal = filesystem.addr_inode_table()
	retVal = pickle.dumps((retVal,state))
	return retVal

def get_data_block(block_number):
        print('+-----'*10)
        print('get_data_block, State: ' + str(state))
        print('+-----'*10)
	passVal = pickle.loads(block_number)
	(retVal,decay)  = filesystem.get_data_block(passVal)
	retVal  = pickle.dumps((retVal,state,decay))
	return retVal

def get_valid_data_block():	
        print('+-----'*10)
        print('get_valid_data_block')
        print('+-----'*10)
	retVal = filesystem.get_valid_data_block()
	retVal = pickle.dumps((retVal,state))
	return retVal

def free_data_block(block_number):  
        print('+-----'*10)
        print('free_data_block')
        print('+-----'*10)
	passVal = pickle.loads(block_number)
	retVal  = filesystem.free_data_block(passVal)
	retVal  = pickle.dumps((retVal,state))
	return retVal

def update_data_block(block_number, block_data):	
        print('+-----'*10)
        print('update_data_block')
        print('+-----'*10)
	passVal1 = pickle.loads(block_number)
	passVal2 = pickle.loads(block_data)
	retVal 	 = filesystem.update_data_block(passVal1, passVal2)
	retVal   = pickle.dumps((retVal,state))
	return retVal

def update_inode_table(inode, inode_number):
        print('+-----'*10)
        print('update_inode_table')
        print('+-----'*10)
	passVal1 = pickle.loads(inode)
	passVal2 = pickle.loads(inode_number)
	retVal 	 = filesystem.update_inode_table(passVal1, passVal2)
	retVal   = pickle.dumps((retVal,state))
	return retVal

def inode_number_to_inode(inode_number):
        print('+-----'*10)
        print('inode_number_to_inode')
        print('+-----'*10)
	passVal = pickle.loads(inode_number)
	retVal  = filesystem.inode_number_to_inode(passVal)
	retVal  = pickle.dumps((retVal,state))
	return retVal

def status():
        print('+-----'*10)
        print('status')
        print('+-----'*10)
	retVal = filesystem.status()
	retVal = pickle.dumps((retVal,state))
	return retVal

def corruptData():
        print('+-----'*10)
        print('corruptData'+str(portNumber))
        print('+-----'*10)
	global state
        state = False
	retVal = 'Data Corrupted in server ' + str(portNumber)
	retVal = pickle.dumps((retVal,state))
	return retVal

def corruptDataBlock(dataBlock):
	passVal = pickle.loads(dataBlock)
	print('+-----'*10)
        print('corruptDatablock'+str(passVal))
        print('+-----'*10)
	retVal = filesystem.corrupt_data_block(passVal)
	print("Data Corrupted!")
	retVal = 'Data Corrupted in server ' + str(portNumber)
	retVal = pickle.dumps((retVal,state))
	return retVal

def rf():
    filesystem.rf()
    return pickle.dumps(0)

def kill():
        print('+-----'*10)
        print('kill')
        print('+-----'*10)
        global Quit
        Quit = 1
        return pickle.dumps(0)

portNumber = int(sys.argv[1])
#portNumber = 8000
server = SimpleXMLRPCServer(("localhost",portNumber))
print ("Listening on port " + str(portNumber) +   "...")

server.register_function(corruptData, 			"corruptData")
server.register_function(corruptDataBlock, 		"corruptDataBlock")
server.register_function(configure, 		   	"configure")
server.register_function(Initialize, 		   	"Initialize")
server.register_function(addr_inode_table, 	   	"addr_inode_table")
server.register_function(get_data_block, 	   	"get_data_block")
server.register_function(get_valid_data_block, 	        "get_valid_data_block")
server.register_function(free_data_block, 		"free_data_block")
server.register_function(update_data_block, 	        "update_data_block")
server.register_function(update_inode_table, 	        "update_inode_table")
server.register_function(inode_number_to_inode,         "inode_number_to_inode")
server.register_function(status, 			"status")
server.register_function(kill,                          "kill")
server.register_function(rf,                            "rf")
#server.serve_forever()

while not Quit: server.handle_request()
