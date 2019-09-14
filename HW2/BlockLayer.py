'''
THIS MODULE IS THE BLOCK LAYER OF THE FILE SYSTEM. IT ONLY DEALS WITH THE BLOCKS. THIS IS THE LOWEST LAYER OF THE FILE SYSTEM AND USES
HANDLE OF CLIENT STUDB TO CALL API FUNCTIONS OF STUB TO CONTACT TO SERVER.

'''
import MemoryInterface

class BlockLayer():

    #RETURNS DATA BLOCK FROM THE BLOCK NUMBER
    def BLOCK_NUMBER_TO_DATA_BLOCK(self, block_number):
        return ''.join(MemoryInterface.get_data_block(block_number))


    #PROVIDES DATA AND BLOCK NUMBER ON WHICH DATA IS TO BE WRITTEN
    def update_data_block(self, block_number, block_data):
        MemoryInterface.update_data_block(block_number, block_data)


    #ASKS FOR VALID DATA BLOCK NUMBER
    def get_valid_data_block(self):
        return MemoryInterface.get_valid_data_block()


    #REMOVES THE INVALID BLOCK NUMBER. 
    def free_data_block(self, block_number):
        MemoryInterface.free_data_block(block_number)


    