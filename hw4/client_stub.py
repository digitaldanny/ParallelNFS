# SKELETON CODE FOR CLIENT STUB HW4
import xmlrpclib, config, pickle

class client_stub():

    def __init__(self):
        self.proxy = xmlrpclib.ServerProxy("http://localhost:8000/")


    # DEFINE FUNCTIONS HERE

    # example provided for initialize
    def Initialize(self):
        try :
            self.proxy.Initialize()
        except Exception as err :
            # print error message
            print "**ERROR CONNECTING TO SERVER**: " + str(err.message)
            print "ARGS: " + str(err.args)
            quit()

    '''
    SUMMARY: RPC wrapper functions
    These functions are wrappers to the client side of the remote file system. They
    serialize all requests, send to the server, and deserialize responses. If the
    server fails at some point, these functions will return -1.
    '''
    def inode_number_to_inode(self, inode_number):
        deserialized = self.__proxyFunction(self.proxy.inode_number_to_inode, inode_number)
        return deserialized
    
    def get_data_block(self, block_number):
        deserialized = self.__proxyFunction(self.proxy.get_data_block, block_number)
        return deserialized
    
    def get_valid_data_block(self):
        try:
            rx = self.proxy.get_valid_data_block()
            deserialized = pickle.loads(rx)
            return deserialized
        except Exception:
            print "ERROR (status): Server failure.."
            return -1 
    
    def free_data_block(self, block_number):
        deserialized = self.__proxyFunction(self.proxy.free_data_block, block_number)
        return deserialized
    
    def update_data_block(self, block_number, block_data):
        try:
            serialIn1 = pickle.dumps(block_number)
            serialIn2 = pickle.dumps(block_data)
            rx = self.proxy.update_data_block(serialIn1, serialIn2)
            deserialized = pickle.loads(rx)
            return deserialized
        except Exception:
            print "ERROR (status): Server failure.."
            return -1 
    
    def update_inode_table(self, inode, inode_number):
        try:
            serialIn1 = pickle.dumps(inode)
            serialIn2 = pickle.dumps(inode_number)
            rx = self.proxy.update_inode_table(serialIn1, serialIn2)
            deserialized = pickle.loads(rx)
            return deserialized
        except Exception:
            print "ERROR (status): Server failure.."
            return -1 
    
    
    def status(self):
        try:
            rx = self.proxy.status()
            return pickle.loads(rx)
        except Exception:
            print "ERROR (status): Server failure.."
            return -1      
    
    '''
    SUMMARY: __proxyFunction
    This function serializes client requests before sending to the client. After receiving
    a response, it deserializes the response.
    '''
    def __proxyFunction(self, function, message):
        try:
            serialMessage = pickle.dumps(message)
            rx = function(serialMessage)
            deserialized = pickle.loads(rx)
            return deserialized
        except Exception:
            print "ERROR: Server failure.."
            return -1


