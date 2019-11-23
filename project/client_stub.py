# SKELETON CODE FOR CLIENT STUB HW4
import xmlrpclib, config, pickle, math

N       = 4     # number of servers running RAID-5
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
        self.proxy = [None for i in range(0, 3)]
        
        for i in range(0, N-1):
            proxyName = "http://localhost:" + str(port + i) + "/"
            self.proxy[i] = xmlrpclib.ServerProxy(proxyName)


    # DEFINE FUNCTIONS HERE

    # example provided for initialize
    def Initialize(self):
        try:
            for i in range(0, N-1):
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
    def status(self):
        try:
            rx = self.proxy[0].status()
            return pickle.loads(rx)
        except Exception:
            print "ERROR (status): Server failure.."
            return -1     

    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                            BLOCK FUNCTIONS
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
        
    def get_data_block(self, block_number):
        try:
            serialMessage = pickle.dumps(block_number)
            p = self.__proxy_of_virtual_block(block_number)
            rx = p.get_data_block(serialMessage)
            deserialized = pickle.loads(rx)
            return deserialized
        except Exception:
            print "ERROR (get_data_block): Server failure.."
            return -1
    
    def get_valid_data_block(self):
        try:
            p = self.__proxy_of_virtual_block(self.virtual_block_size*self.distribute_load)
            rx = p.get_valid_data_block()
            deserialized = pickle.loads(rx)
            
            # map physical block number to virtual block number before returning
            # to the client.
            serverNum = self.distribute_load
            pBlockNum = deserialized 
            virtual_block_number = self.__translate_physical_to_virtual_block(serverNum, pBlockNum)
            
            # this function distributes the load of the servers by incrementing
            # which server returns a new block number every time this function
            # is called.
            if self.distribute_load < N-1:
                self.distribute_load += 1 
            else:
                self.distribute_load = 0
                
            return virtual_block_number
        except Exception:
            print "ERROR (get_valid_data_block): Server failure.."
            return -1 
    
    def free_data_block(self, block_number):
        try:
            serialMessage = pickle.dumps(block_number)
            p = self.__proxy_of_virtual_block(block_number)
            rx = p.free_data_block(serialMessage)
            deserialized = pickle.loads(rx)
            return deserialized
        except Exception:
            print "ERROR (free_data_block): Server failure.."
            return -1
    
    def update_data_block(self, block_number, block_data):
        try:
            serialIn1 = pickle.dumps(block_number)
            serialIn2 = pickle.dumps(block_data)
            p = self.__proxy_of_virtual_block(block_number)
            rx = p.update_data_block(serialIn1, serialIn2)
            deserialized = pickle.loads(rx)
            return deserialized
        except Exception:
            print "ERROR (update_data_block): Server failure.."
            return -1 
    
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                            INODE FUNCTIONS
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    
    def inode_number_to_inode(self, virtual_inode_number):
	print("CS: inode_number_to_inode")
	print(self.__physical_inode_of_virtual_inode(virtual_inode_number), virtual_inode_number)
	p = self.__proxy_of_virtual_inode(virtual_inode_number)
        print(p)
	try:
            serialMessage = pickle.dumps(self.__physical_inode_of_virtual_inode(virtual_inode_number))
            p = self.__proxy_of_virtual_inode(virtual_inode_number)
            print(p)
            rx = p.inode_number_to_inode(serialMessage)
            deserialized = pickle.loads(rx)
	    #print("deserialized: ", deserialized)
	    #desearialized contains retVal, state - when retVal is true, server is working
            return deserialized[0]
        except Exception:
            print "ERROR (inode_number_to_inode): Server failure.."
            return -1
    
    def update_inode_table(self, inode, virtual_inode_number):
        try:
            serialIn1 = pickle.dumps(inode)
            serialIn2 = pickle.dumps(self.__physical_inode_of_virtual_inode(virtual_inode_number))
	    for i in range(0, N-1):
                p = self.proxy[i]
                rx = p.update_inode_table(serialIn1, serialIn2)
            deserialized = pickle.loads(rx)
	    #deserialized = (retVal,state)
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
	#print(serverNum, localBlockNum, virtual_block_num)
        return (serverNum, localBlockNum)
    
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
	#print("Made it")
        serverNum = self.__translate_virtual_to_physical_block(virtual_block_number)
	#print("serverNum: ", serverNum)
        return self.proxy[serverNum[0]]

    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                          INODE NUMBER MAPPING
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+

    '''
    SUMMARY: __translate_virtual_to_physical_inode
    Translates a virtual inode number to a physical inode number and the port 
    offset for the target server.
    '''
    def __translate_virtual_to_physical_inode(self, virtual_inode_num):
        serverNum = (int)(math.floor(virtual_inode_num/self.virtual_inode_size))
        localInodeNum = virtual_inode_num % self.virtual_inode_size
        return (serverNum, localInodeNum)
    
    '''
    SUMMARY: __translate_physical_to_virtual_inode
    Translates physical inode number and server number it comes from to a virtual
    inode number to be used in the client filesystem.
    '''
    def __translate_physical_to_virtual_inode(self, server_num, physical_inode_num):
        return (server_num * self.virtual_inode_size) + physical_inode_num

    '''
    SUMMARY: __proxy_of_virtual_inode
    Returns proxy object from the server's proxy list based on the virtual inode
    number passed in.
    '''
    def __proxy_of_virtual_inode(self, virtual_inode_number):
	#print("__proxy_of_virtual_inode")
        serverNum = self.__translate_virtual_to_physical_inode(virtual_inode_number)
	#print("serverNum: ", serverNum)
        return self.proxy[serverNum[0]]

    '''
    SUMMARY: __physical_inode_of_virtual_inode
    Returns physical inode object based on the virtual inode number passed in.
    '''
    def __physical_inode_of_virtual_inode(self, virtual_inode_number):
	#print("__physical_inode_of_virtual_inode")
        serverNum = self.__translate_virtual_to_physical_inode(virtual_inode_number)
	#print("serverNum: ", serverNum)
        return serverNum[1]
