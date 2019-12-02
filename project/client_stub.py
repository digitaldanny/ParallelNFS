# SKELETON CODE FOR CLIENT STUB HW4
import xmlrpclib, config, pickle, math

N       = 4     # number of servers running RAID-5
port    = 8000  # starting port number to initialize proxies
PREV 	= 'P'
NEXT 	= 'N'

'''
SUMMARY: client_stub
This layer maps from virtual inode numbers / block numbers to physical inode
numbers and block numbers on the individual servers.
'''
class client_stub():

	'''
	SUMMARY: __init__
	Initialize proxies, etc..
	
	NOTE:
	This function initially claims ~TOTAL_NO_OF_BLOCKS/N parity blocks. If
	the number is not a multiple of N, claim enough blocks until it is.
	'''
    def __init__(self):
        
        # load configuration file properties
        self.virtual_block_size = config.TOTAL_NO_OF_BLOCKS
        self.virtual_inode_size = config.INODE_SIZE

        # proxies to the servers
        self.proxy = [None for i in range(N)]
        for i in range(N):
            proxyName = "http://localhost:" + str(port + i) + "/"
            self.proxy[i] = xmlrpclib.ServerProxy(proxyName)
			
		# points to the next server to request a data block from
		# (starts at the far end because parity_blocks claims using
		# __prev function).
		self.data_blk_ptr = N-1
			
		# claim the first NUM_BLOCKS/N virtual blocks to use as parity blocks
		self.block_claim_dir = PREV
		self.num_parity_blocks = math.ceil(config.TOTAL_NO_OF_BLOCKS/N)
		
		# if the number of parity blocks is not a multiple of N, continue incrementing
		# until it is.
		while (self.num_parity_blocks % N > 0):
			self.num_parity_blocks += 1
		
		# claim the parity blocks and switch the direction of block claiming
		self.parity_blocks 	= [None for i in range(self.num_parity_blocks)]
		for i in range(self.num_parity_blocks):
			self.parity_blocks[i] = self.get_valid_data_block()
			
		self.block_claim_dir = NEXT
		print("NUMBER OF PARITY BLOCKS CLAIMED: " + str(self.num_parity_blocks))

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

    '''
    SUMMARY: RPC wrapper functions
    These functions are wrappers to the client side of the remote file system. They
    serialize all requests, send to the server, and deserialize responses. If the
    server fails at some point, these functions will return -1.
    '''
    def status(self):
        try:
            rx = ''
            for i in range(N):
                #rx += "+-----------------------------------------+"
                #rx += "PORT NUM: " + str(port + i)
                #rx += "+-----------------------------------------+"
                rx += self.proxy[i].status()
            return pickle.loads(rx)
        except Exception:
            print "ERROR (status): Server failure.."
            return -1  

    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    #                            BLOCK FUNCTIONS
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
        
	'''
	SUMMARY: get_data_block
	Return the contents of a data block on the appropriate server.
	
	NOTE:
	This function handles if the requested server of the virtual block number
	has a failure by reconstructing the data using the blocks from other servers.
	'''
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


	'''
	SUMMARY: get_valid_data_block
	Return the next available virtual block number by incrementing the target
	proxy to request a block from. After requesting a block from each server, 
	the pointer will wrap back to 0.
	'''
    def get_valid_data_block(self):

        try:
            # Retrieve the physical block
            p = self.proxy[self.data_blk_ptr]
            rx = p.get_valid_data_block()
            (blockNum,state) = pickle.loads(rx)
                       
            # map physical block number to virtual block number before returning
            # to the client.
            serverNum = self.data_blk_ptr
            pBlockNum = blockNum 
            virtual_block_number = self.__translate_physical_to_virtual_block(serverNum, pBlockNum)
			
			# point to the next server to write data to..
			# block_claim_dir is changed in the init function so the parity
			# blocks and data blocks are claimed in opposite directions.
			if self.block_claim_dir == NEXT:
				# server pattern: 0, 1, 2, 3,.. 0, 1, 2, 3
				self.data_blk_ptr = self.__next(self.data_blk_ptr)
			else
				# server pattern: 3, 2, 1, 0,.. 3, 2, 1, 0
				self.data_blk_ptr = self.__prev(self.data_blk_ptr)
				
            return virtual_block_number
			
        except Exception:
            print "ERROR (get_valid_data_block): Server failure.."
            return -1 
    
	'''
	SUMMARY: free_data_block
	Deallocate the specified data block.
	
	NOTE:
	This function also reads back the current DATA/PARITY blocks to adjust
	update the parity block.
	'''
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
    
	'''
	SUMMARY: update_data_block
	Write the data block data to the appropriate server.
	
	NOTE:
	This function also reads back the DATA/PARITY blocks to calculate
	and update the parity data.
	
	The steps are labeled as 1,2,3,4 to match guide shown in the lecture
	slides (slide 66 - Parity in RAID 4,5)
	'''
    def update_data_block(self, virtual_block_number, block_data):
        try:
			print("CS: Entered (update_data_block)")
			# read back the current data block contents (1.FIRST READ)
            (serverNumData, pBlockData) = self.__translate_virtual_to_physical_block(virtual_block_number)
			proxyData = self.proxy[serverNumData]				# find server 
			serialBlockNumData = pickle.dumps(pBlockData)		# find physical block number
			
			rx = proxyData.get_data_block(serialBlockNumData)	# request the current data
			currData = pickle.loads(rx)							# convert the string message into real data
			print("CS: Got current data")
			
			# read back the current parity block contents (2. SECOND READ)
			iparity = self.__physical_block_number_to_parity_index(pBlockData, serverNumData)	# parity block list index for specified data block
			vParityNum = self.parity_blocks[iparity]											# virtual parity block number
            (serverNumParity, pParityNum) = self.__translate_virtual_to_physical_block(vParityNum) # find the physical block number and server to read/write
			proxyParity = self.proxy[serverNumParity]											# find server to read/write parity data from
			serialBlockNumData = pickle.dumps(pParityNum)		# serialize data to send to the server
			
			rx = proxyParity.get_data_block(serialBlockNumData)	# request the current parity data
			currParity = pickle.loads(rx)						# convert the string message into real data
			print("CS: Got current parity")
			
			# calculate the new parity block contents
			print("CURRENT DATA")
			print(currData)
			
			print("CURRENT PARITY")
			print(currParity)
			newParity = currParity
			
			# update the parity block contents (4. FIRST WRITE)
			serialBlockNum = pickle.dumps(pParityNum)
            serialBlockData = pickle.dumps(newParity)
            rx = proxyParity.update_data_block(serialBlockNum, serialBlockData)
			print("CS: Updated parity")
			
			# update the data block with new data (3. SECOND WRITE)
            serialBlockNum = pickle.dumps(pBlockData)
            serialBlockData = pickle.dumps(block_data)
            rx = proxyData.update_data_block(serialBlockNum, serialBlockData)
            deserialized = pickle.loads(rx)
			print("CS: Updated data")
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
    #                          PARITY BLOCK MAPPING
    # +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
	
	'''
	SUMMARY: __next
    This function handles the wrap around for picking which server's 
    is pointed at.
	'''
    def __next(self, ptr):
        if ptr < N-1:
            ptr += 1 
        else:
            ptr = 0
        return ptr
		
	'''
	SUMMARY: __prev
	'''
    def __prev(self, ptr):
        if ptr > 0:
            ptr -= 1 
        else:
            ptr = N-1
        return ptr
	
	'''
	SUMMARY: __physical_block_number_to_parity_index
	Maps physical block number and server number to the appropriate parity block's 
	index.
	'''
	def __physical_block_number_to_parity_index(self, physical_block_num, server_num):
		return 0
        
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

