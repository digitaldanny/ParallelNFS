# SKELETON CODE FOR CLIENT STUB HW4
import xmlrpclib, config, pickle, math

N       = 2     # number of pairs of servers running RAID-1
port    = 8000  # starting port number to initialize proxies

'''
SUMMARY: client_stub
This layer maps from virtual inode numbers / block numbers to physical inode
numbers and block numbers on the individual servers.
'''
class client_stub():

    def __init__(self):
        self.distribute_load = 0
        self.virtual_block_size = config.TOTAL_NO_OF_BLOCKS
        self.virtual_inode_size = config.INODE_SIZE
        
        self.proxy = [None for i in range(N*2)]
        for i in range(N*2):
            proxyName = "http://localhost:" + str(port + i) + "/"
            self.proxy[i] = xmlrpclib.ServerProxy(proxyName)
	print(self.proxy)


    # DEFINE FUNCTIONS HERE

    # example provided for initialize
    def Initialize(self):
	print("client_stub: Initialize()")
        try:
            for i in range(N*2):
                self.proxy[i].Initialize()
        
        except Exception as err :
            # print error message
            print "**ERROR CONNECTING TO SERVER**: " + str(err.message)
            print "ARGS: " + str(err.args)
            #quit()

    '''
    SUMMARY: RPC wrapper functions
    These functions are wrappers to the client side of the remote file system. They
    serialize all requests, send to the server, and deserialize responses. If the
    server fails at some point, these functions will return -1.
    '''
    def status(self, server):
        try:
            rx = ''
            rx = self.proxy[server].status()
            return pickle.loads(rx)
        except Exception:
            print "ERROR (status): Server failure.."
            return -1   

    # requests servers to shut down
    def kill_all(self):
        for i in range(N*2):
            self.proxy[i].kill()			

    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                            BLOCK FUNCTIONS
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
        
    def get_data_block(self, virtual_block_number):
	try:
	    (serverNum,physicalBlock) = self.__translate_virtual_to_physical_block(virtual_block_number)
            serialMessage = pickle.dumps(physicalBlock)
	    for i in range(2):
		p = self.proxy[serverNum*2 + i]
                rx = p.get_data_block(serialMessage)
                deserialized = pickle.loads(rx)
		print("Fetching data block " + str(physicalBlock) + " on server " + str(serverNum*2 + i))
		if(deserialized[2] == True):
		    #data has decayed
		    #fail the read
		    print "ERROR (get_data_block): Server data decay failure, reconstructing data.."
		    print("Fetching data block " + str(physicalBlock) + " on server " + str(serverNum*2 + 1 - i))
		    #read correct data from other server
		    p1 = self.proxy[serverNum*2 + 1-i]
		    rx = p1.get_data_block(serialMessage)
		    message = pickle.loads(rx)
		    #write data back to corrupted block
		    print("Updating data block " + str(physicalBlock) + " on server " + str(serverNum*2 + i))
		    serialIn1 = pickle.dumps(physicalBlock)
            	    serialIn2 = pickle.dumps(message[0])
		    p.update_data_block(serialIn1,serialIn2)
		    return message[0]
		#if state is true, then return message. If False server failed and read from other server in pair
		if(deserialized[1] == True): break
		print("Server " + str(serverNum*2) + " failure!!!")
            return deserialized[0]
        except Exception:
            print "ERROR (get_data_block): Server failure.."
            return -1
    
    def get_valid_data_block(self):
        try:
	    #Retrieve two data blocks at the same time on the pair of servers
            p = self.proxy[self.distribute_load*2]
	    p1 = self.proxy[self.distribute_load*2 + 1]
            rx = p.get_valid_data_block()
	    rx1 = p1.get_valid_data_block()
            (blockNum,state) = pickle.loads(rx)
	    print("Fetching new data block " + str(blockNum) + " on servers " + str(self.distribute_load*2) + " and " + str(self.distribute_load*2 + 1))
            # map physical block number to virtual block number before returning
            # to the client.
            serverNum = self.distribute_load
            pBlockNum = blockNum 
            virtual_block_number = self.__translate_physical_to_virtual_block(serverNum, pBlockNum)
            
            # this function distributes the load of the servers by incrementing
            # which server returns a new block number every time this function
            # is called.
            if self.distribute_load < N:
                self.distribute_load += 1 
            else:
                self.distribute_load = 0
                
            return virtual_block_number
        except Exception:
            print "ERROR (get_valid_data_block): Server failure.."
            return -1 
    
    def free_data_block(self, virtual_block_number):
	try:
	    (serverNum,physicalBlock) = self.__translate_virtual_to_physical_block(virtual_block_number)
            serialMessage = pickle.dumps(physicalBlock)
	    #Free two data blocks at the same time on the pair of servers
	    print("Freeing data block " + str(physicalBlock) + " on servers " + str(serverNum) + " and " + str(serverNum+1))
            p1 = self.proxy[serverNum*2]
	    p2 = self.proxy[serverNum*2 + 1]
            rx1 = p1.free_data_block(serialMessage)
	    rx2 = p2.free_data_block(serialMessage)
            deserialized = pickle.loads(rx1)
            return deserialized[0]
        except Exception:
            print "ERROR (free_data_block): Server failure.."
            return -1
    
    def update_data_block(self, virtual_block_number, block_data):
        try:
	    (serverNum,physicalBlock) = self.__translate_virtual_to_physical_block(virtual_block_number)
            serialIn1 = pickle.dumps(physicalBlock)
            serialIn2 = pickle.dumps(block_data)
	    #Update two data blocks at the same time on the pair of servers
	    print("Updating data block " + str(physicalBlock) + " on servers " + str(serverNum) + " and " + str(serverNum+1))
            p1 = self.proxy[serverNum*2]
	    p2 = self.proxy[serverNum*2 + 1]
            rx1 = p1.update_data_block(serialIn1, serialIn2)
	    rx2 = p2.update_data_block(serialIn1, serialIn2)
            deserialized = pickle.loads(rx1)
            return deserialized[0]
        except Exception:
            print "ERROR (update_data_block): Server failure.."
            return -1 
    
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                            INODE FUNCTIONS
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    
    def inode_number_to_inode(self, inode_number):
	try:
            serialMessage = pickle.dumps(inode_number)
	    for i in range(N*2):
		p = self.proxy[i]
                rx = p.inode_number_to_inode(serialMessage)
                deserialized = pickle.loads(rx)
		if(deserialized[1] == True): break
            return deserialized[0]
        except Exception:
            print "ERROR (inode_number_to_inode): Server failure.."
            return -1
    
    def update_inode_table(self, inode, inode_number):
        try:
            serialIn1 = pickle.dumps(inode)
            serialIn2 = pickle.dumps(inode_number)
	    for i in range(N*2):
                p = self.proxy[i]
                rx = p.update_inode_table(serialIn1, serialIn2)
            deserialized = pickle.loads(rx)
            return deserialized[0]
        except Exception:
            print "ERROR (update_inode_table): Server failure.."
            return -1 
     
        
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                          BLOCK NUMBER MAPPING
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    
    '''
    SUMMARY: __translate_virtual_to_physical_block
    Translates a virtual block number to a physical block number and the port 
    offset for the target server.
    '''
    def __translate_virtual_to_physical_block(self, virtual_block_num):
        serverNum = (int)(math.floor(virtual_block_num/self.virtual_block_size))
        localBlockNum = virtual_block_num % self.virtual_block_size
        return (serverNum*2, localBlockNum)
    
    '''
    SUMMARY: __translate_physical_to_virtual_block
    Translates physical block number and server number it comes from to a virtual
    block number to be used in the client filesystem.
    '''
    def __translate_physical_to_virtual_block(self, server_num, physical_block_num):
        return (server_num * self.virtual_block_size) + physical_block_num

    '''
    SUMMARY: __proxy_of_virtual_block
    Returns proxy object from the server's proxy list based on the virtual block
    number passed in.
    '''
    def __proxy_of_virtual_block(self, virtual_block_number):
        serverNum = self.__translate_virtual_to_physical_block(virtual_block_number)
        return self.proxy[serverNum[0]*2]
