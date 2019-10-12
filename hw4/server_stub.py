# SKELETON CODE FOR SERVER STUB HW4
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import time, Memory, pickle , InodeOps, config, DiskLayout


filesystem = Memory.Operations()

# FUNCTION DEFINITIONS 

# example provided for initialize
def Initialize():
	retVal = Memory.Initialize()
	retVal = pickle.dumps(retVal)
	return retVal


''' WRITE CODE HERE FOR REST OF FUNCTIONS'''



server = SimpleXMLRPCServer(("",8000))
print ("Listening on port 8000...")

# REGISTER FUNCTIONS

#example provided for initialize
server.register_function(Initialize, 		   	"Initialize")

''' WRITE CODE HERE FOR REST OF REGISTER CALLS '''

# run the server
server.serve_forever()














