# SKELETON CODE FOR SERVER STUB HW4
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import time, Memory, pickle , InodeOps, config, DiskLayout


filesystem = Memory.Operations()

# example provided for initialize
def Initialize():
    print "CALLED: Initialize()"
    print "+-----"*10
    retVal = Memory.Initialize()
    retVal = pickle.dumps(retVal)
    return retVal

'''
SUMMARY: Memory wrapper functions
These functions deserialize requests from a client using pickle.loads(request), passes
the request through to the Memory layer, and serializes the response before returning
to the client.
'''
def addr_inode_table():
    print "+-----"*10
    print "CALLED: addr_inode_table()"
    tx = filesystem.addr_inode_table()
    return pickle.dumps(tx)

def get_data_block(block_number):
    print "+-----"*10
    print "CALLED: get_data_block()"
    deserialized = pickle.loads(block_number)
    tx = filesystem.get_data_block(deserialized)
    return pickle.dumps(tx)

def get_valid_data_block():
    print "+-----"*10
    print "CALLED: get_valid_data_block()"
    tx = filesystem.get_valid_data_block()
    return pickle.dumps(tx)

def free_data_block(block_number):
    print "+-----"*10
    print "CALLED: free_data_block()"
    deserialized = pickle.loads(block_number)
    tx = filesystem.free_data_block(deserialized)
    return pickle.dumps(tx)

def update_data_block(block_number, block_data):
    print "+-----"*10
    print "CALLED: update_data_block()"
    deserialized1 = pickle.loads(block_number)
    deserialized2 = pickle.loads(block_data)
    tx = filesystem.update_data_block(deserialized1, deserialized2)
    serial = pickle.dumps(tx)
    return serial

def update_inode_table(inode, inode_number):
    print "+-----"*10
    print "CALLED: update_inode_table()"
    deserialized1 = pickle.loads(inode)
    deserialized2 = pickle.loads(inode_number)
    tx = filesystem.update_inode_table(deserialized1, deserialized2)
    serial = pickle.dumps(tx)
    return serial

def inode_number_to_inode(inode_number):
    print "+-----"*10
    print "CALLED: inode_number_to_inode()"
    deserialized = pickle.loads(inode_number)
    tx = filesystem.inode_number_to_inode(deserialized)
    serial = pickle.dumps(tx)
    return serial

def status():
    print "+-----"*10
    print "CALLED: status()"
    tx = filesystem.status()
    return pickle.dumps(tx)

'''
SCRIPT BEGIN:
This script makes a connection to the client, registers all Memory wrapper functions
listed above, and serves forever.
'''
server = SimpleXMLRPCServer(("",8000))
print ("Listening on port 8000...")

# register all functions in the server
server.register_function(Initialize,            "Initialize")
server.register_function(addr_inode_table,      "addr_inode_table")
server.register_function(get_data_block,        "get_data_block")
server.register_function(get_valid_data_block,  "get_valid_data_block")
server.register_function(free_data_block,       "free_data_block")
server.register_function(update_data_block,     "update_data_block")
server.register_function(update_inode_table,    "update_inode_table")
server.register_function(inode_number_to_inode, "inode_number_to_inode")
server.register_function(status,                "status")

# run the server
server.serve_forever()













