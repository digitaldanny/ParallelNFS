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
	
        # block map is used for checking that the parity/data blocks were configured properly
        self.block_map_pcnt = 0	# parity block count
        self.block_map_dcnt = 0	# data block count
        self.block_map_tcnt = 0 # total number of blocks in map
        self.block_map = ['' for i in range(N*config.TOTAL_NO_OF_BLOCKS)]
        
        # load distribution parameters
        self.parity_blocks 	= [-1 for i in range(config.TOTAL_NO_OF_BLOCKS)]
        self.data_blk_ptr 	= 0 # first data block claimed will be at index 0
        self.parity_blk_ptr = 1 # parity block always starts 1 over
        
        # load configuration file properties
        self.virtual_block_size = config.TOTAL_NO_OF_BLOCKS
        self.virtual_inode_size = config.INODE_SIZE

        # proxies to the servers
        self.proxy = [None for i in range(N)]
        for i in range(N):
            proxyName = "http://localhost:" + str(port + i) + "/"
            self.proxy[i] = xmlrpclib.ServerProxy(proxyName)

    # initialize the servers
    def Initialize(self):
        try:
            for i in range(N):
                self.proxy[i].Initialize()
        
        except Exception as err :
            # print error message
            print "**ERROR CONNECTING TO SERVER**: " + str(err.message)
            print "ARGS: " + str(err.args)
            #quit()
            
    # requests servers to shut down
    def kill_all(self):
        for i in range(N):
            self.proxy[i].kill()
	
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                            DEBUG MAP FUNCTIONS
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+	
    '''
    SUMMARY: check_map
    Print out the parity and data block map for debugging.
    '''
    def check_map(self):
        
        # determine how much of the array to display to the user
        for i in range(int(math.ceil(self.block_map_tcnt/N))):
            array = ['' for j in range(N)]
            
            # place parts of the block map into the string to be displayed
            for j in range(N):
                array[j] = self.block_map[N*i + j]
                
            print(' | '.join(array))

    '''
    SUMMARY: add_to_debug_map
    Add a new element to the debugger map.
    type 	- 'D' => data
                    - 'P' => parity
    '''
    def add_to_debug_map(self, t):
        sym = 'XX'
        if t  == 'D':
            sym = t + str(self.block_map_dcnt)
            self.block_map_dcnt += 1
                
        elif t == 'P':
            sym = t + str(self.block_map_pcnt)
            self.block_map_pcnt += 1
        
        self.block_map[self.block_map_tcnt] = sym
        self.block_map_tcnt += 1

    '''
    SUMMARY: RPC wrapper functions
    These functions are wrappers to the client side of the remote file system. They
    serialize all requests, send to the server, and deserialize responses. If the
    server fails at some point, these functions will return -1.
    '''
    def status(self):
        self.check_map()
        # try:
        #     rx = ''
        #     for i in range(N):
        #         #rx += "+-----------------------------------------+"
        #         #rx += "PORT NUM: " + str(port + i)
        #         #rx += "+-----------------------------------------+"
        #         rx += self.proxy[i].status()
        #     return pickle.loads(rx)
        # except Exception:
        #     print "ERROR (status): Server failure.."
        #     return -1  

    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                            BLOCK FUNCTIONS
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
        
    def get_data_block(self, virtual_block_number):
        try:
            (serverNum,physicalBlock) = self.__translate_virtual_to_physical_block(virtual_block_number)
            serialMessage = pickle.dumps(physicalBlock)
            p = self.proxy[serverNum]
            rx = p.get_data_block(serialMessage)
            deserialized = pickle.loads(rx)
            return deserialized[0]
        except Exception:
            print "ERROR (get_data_block): Server failure.."
            return -1

    def get_valid_data_block(self):
	
        '''
        SUMMARY: __next
        This function handles the wrap around for picking which server's 
        get_valid_data_block function from.
        '''
        def __next(ptr):
            if ptr < N-1:
                ptr += 1 
            else:
                ptr = 0
            return ptr

        try:
            # DATA/PARITY BLOCK RETREIVE ---------------------------------------------
            p = self.proxy[self.data_blk_ptr]
            rx = p.get_valid_data_block()
            (blockNum,state) = pickle.loads(rx)
            self.add_to_debug_map('D') # for debug purposes
            
            # map physical block number to virtual block number before returning
            # to the client.
            serverNum = self.data_blk_ptr
            pBlockNum = blockNum 
            virtual_block_number = self.__translate_physical_to_virtual_block(serverNum, pBlockNum)
			
            # instantiate a new parity block if it does not exist for
            # this physical block number.
            print("CS: physical block num: " + str(pBlockNum))
            print("CS: parity_blocks[pBlockNum] = " + str(self.parity_blocks[pBlockNum]))
            if self.parity_blocks[pBlockNum] == -1:
        
                # parity block DNE -> create a new parity block
                p = self.proxy[self.parity_blk_ptr]
                
                # get a new block number to be used for parity
                rx = p.get_valid_data_block()
                
                # get the virtual block number
                (physParityBlockNum,state) = pickle.loads(rx)	# phys block num
                serverNum = self.parity_blk_ptr					# server num
                virtual_parity_block_number = self.__translate_physical_to_virtual_block(serverNum, physParityBlockNum)
                
                # save the parity block's virtual address
                self.parity_blocks[pBlockNum] = virtual_parity_block_number
                self.add_to_debug_map('P') # for debug purposes

            # POINTER HANDLING -------------------------------------------------------
            # this function distributes the load of the servers by incrementing
            # which server returns a new block number every time this function
            # is called.
            self.data_blk_ptr = __next(self.data_blk_ptr)
                
            # parity block always has priority so data block pointer should skip
            # if they are equal.
            if self.data_blk_ptr == self.parity_blk_ptr:
                self.data_blk_ptr = __next(self.data_blk_ptr)
                    
            # parity points to the next block every new offset (when ServerNum == 0)
            if self.data_blk_ptr == 0:
                self.parity_blk_ptr = __next(self.parity_blk_ptr)
    
            return virtual_block_number
			
        except Exception:
            print "ERROR (get_valid_data_block): Server failure.."
            return -1 
    
    def free_data_block(self, virtual_block_number):
        (serverNum,physicalBlock) = self.__translate_virtual_to_physical_block(virtual_block_number)
        serialMessage = pickle.dumps(physicalBlock)
        p = self.proxy[serverNum]
		
        try:
            (serverNum,physicalBlock) = self.__translate_virtual_to_physical_block(virtual_block_number)
            serialMessage = pickle.dumps(physicalBlock)
            p = self.proxy[serverNum]
            rx = p.free_data_block(serialMessage)
            deserialized = pickle.loads(rx)
            return deserialized[0]
        except Exception:
            print "ERROR (free_data_block): Server failure.."
            return -1
    
    def update_data_block(self, virtual_block_number, block_data):
        try:
            (serverNum,physicalBlock) = self.__translate_virtual_to_physical_block(virtual_block_number)
            serialIn1 = pickle.dumps(physicalBlock)
            serialIn2 = pickle.dumps(block_data)
            p = self.proxy[serverNum]
            rx = p.update_data_block(serialIn1, serialIn2)
            deserialized = pickle.loads(rx)
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
	    for i in range(N):
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
	    for i in range(N):
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
        serverNum = self.__translate_virtual_to_physical_block(virtual_block_number)
        return self.proxy[serverNum[0]]

