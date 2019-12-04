import time, MemoryInterface, AbsolutePathNameLayer, client_stub, client_stub_RAID_1, sys

'''
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
CONFIGURATIONS
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
mode -  0: command line mode for final project
        1: testbench mode
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''
mode    = 0
RAID	= 5

'''
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
CONSTANTS
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''
EXIT    = 'exit'
MKDIR   = 'mkdir'
CREATE  = 'create'
MV      = 'mv'
READ    = 'read'
WRITE   = 'write'
STATUS  = 'status'
RM      = 'rm'
TEST    = 'test'

def Initialize_My_FileSystem():
    MemoryInterface.Initialize_My_FileSystem()
    AbsolutePathNameLayer.AbsolutePathNameLayer().new_entry('/', 1)

#HANDLE TO ABSOLUTE PATH NAME LAYER
interface = AbsolutePathNameLayer.AbsolutePathNameLayer()

class FileSystemOperations():

    #MAKES NEW DIRECTORY
    def mkdir(self, path):
        interface.new_entry(path, 1)

    #CREATE FILE
    def create(self, path):
        interface.new_entry(path, 0)
        

    #WRITE TO FILE
    def write(self, path, data, offset=0):
        interface.write(path, offset, data)
      

    #READ
    def read(self, path, offset=0, size=-1):
        read_buffer = interface.read(path, offset, size)
        if read_buffer != -1: print(path + " : " + read_buffer)

    
    #DELETE
    def rm(self, path):
        interface.unlink(path)


    #MOVING FILE
    def mv(self, old_path, new_path):
        interface.mv(old_path, new_path)


    #CHECK STATUS
    def status(self, server):
	print("++++++++++++++"*5)
        print("Status for Server " + str(server))
        print("++++++++++++++"*5)
        print(MemoryInterface.status(server))
        
    def kill_all(self):
        MemoryInterface.kill_all()

def printDivider():
    print("+====="*10 + "+")

def announce(msg):
    printDivider()
    print(msg)
    printDivider()

def endit():
    print "Ending program..."
    #quit()
    
'''
SUMMARY: main
This function runs the client interactive window for transmitting
data to the servers.
'''
def main():
    
    Initialize_My_FileSystem()
    fs = FileSystemOperations()
    
    while True:        
        try:
            # split the user's response string by delimiters (white space)
            response = raw_input('$ ').split()
            cmd = response[0]
            if cmd == EXIT:
                # EXIT: Terminate program and all the connected servers.
                fs.kill_all()
                break
            
            elif cmd == MKDIR:
                # MKDIR: Create a new directory.
                directory = response[1]
                fs.mkdir(directory)
                
            elif cmd == CREATE:
                # CREATE: Create a new file.
                filename = response[1]
                fs.create(filename)
                
            elif cmd == MV:
                # MV: Move a file from one directory to another
                # directory location. The filename is optionally
                # allowed to change too.
                originalLocation = response[1]
                newLocation = response[2]
                fs.mv(originalLocation, newLocation)
                
            elif cmd == READ:
                # READ: Read a length of a file from the file
                # system.
                filename = response[1]
                offset = int(response[2])
                length = int(response[3])
                fs.read(filename, offset, length)
                
            elif cmd == WRITE:
                # WRITE: Write a string (packed between quotations)
                filename = response[1]
                msg = ' '.join(response[2:-1])
                offset = int(response[-1])
                fs.write(filename, msg, offset)
                
            elif cmd == STATUS:
                # STATUS:
                fs.status(int(response[1]))
                
            elif cmd == RM:
                # RM: Remove a file or directory.
                location = response[1]
                fs.rm(location)
                
            elif cmd == TEST:
                # TEST: This is a dummy function used to quickly
                # set up the file system for testing an input.
                dir1        = '/a'
                dir2        = '/b'
                filename    = '/file.txt'
                msg         = 'Hi this is a test'
                offset      = 0
                
                fs.mkdir(dir1)
                fs.mkdir(dir1 + dir2)
                fs.create(dir1 + dir2 + filename)
                fs.write(dir1 + dir2 + filename, msg, offset)
                fs.read(dir1 + dir2 + filename, offset, 17)
                
            else:
                location = response[1]
                fs.rm(location)
            
        except Exception as err:
            print("Command (" + str(cmd) + ") failed..")
            print("ERROR MESSAGE BELOW:")
            print("++++++++++++++"*5)
            print(err.message)
            print("++++++++++++++"*5)
#
'''
SUMMARY: testbench
This function is the testbench ran on the HW3/4 file system.
'''
def testbench():
    Initialize_My_FileSystem()
    fs = FileSystemOperations()
    
    start = time.time()
    msg = "Hello world! "*50
    
    announce("FILE FAILED CREATION..")
    ret = fs.create('/A/B/file.txt')
    if ret == -1: endit()
    
    announce("DIRECTORIES /A/B and /A/C CREATED..")
    ret = fs.mkdir('/A')
    ret = fs.mkdir('/A/B')
    ret = fs.mkdir('/A/C')
    if ret == -1: endit()
    
    announce("FILE CREATION SUCCESSFUL..")
    ret = fs.create('/A/B/file.txt')
    if ret == -1: endit()

    announce("WRITE COMPLETE..")
    fs.write('/A/B/file.txt', msg, offset=0)
    
    announce("READ COMPLETE..")
    ret = fs.read('/A/B/file.txt', 0, 12)
    if ret == -1: endit()
    
    fs.status()
    
    fs.write('/A/B/file.txt', 'i', offset=1)
    ret = fs.read('/A/B/file.txt', 0, 12)
    if ret == -1: endit()
    
    fs.write('/A/B/file.txt', ' success', offset=2)
    ret = fs.read('/A/B/file.txt', 0, 12)
    if ret == -1: endit()
    
    fs.write('/A/B/file.txt', ' fail', offset=11)
    ret = fs.read('/A/B/file.txt', 0, 12)
    if ret == -1: endit()
    
    fs.status()
    
    # LINK TESTS -------------------------------------------------------
    announce("MOVING FILE TO NEW DIRECTORY")
    fs.mv('/A/B/file.txt', '/A/C/elif.txt')
    fs.status()
    readData = fs.read('/A/C/elif.txt', 0, 100)

    # UNLINK TESTS -----------------------------------------------------
    
    announce("REMOVING DIRECTORY SHOULD FAIL")
    fs.rm('/A/C')
    fs.status()
    
    announce("REMOVING FILE BY UNLINKING")
    fs.rm('/A/C/elif.txt')
    fs.status()
    
    announce("REMOVING NON-ROOT DIRECTORIES SHOULD BE SUCCESSFUL")
    fs.rm('/A/C')
    fs.rm('/A/B')
    fs.rm('/A')
    fs.status()
    
    end = time.time()
    print "RPC TESTBENCH TIME: " + str(end - start)
    
    '''Examples:
    my_object.mkdir("/A")
    my_object.status()
    my_object.mkdir("/B")
    my_object.status()
    my_object.create("/A/1.txt"), as A is already there we can crete file in A
    my_object.status()
    my_object.write("A/1.txt", "POCSD", offset), as 1.txt is already created now, we can write to it.
    my_object.status()
    my_object.mv("/A/1.txt", "/B")
    my_object.status()
    my_object.rm("A/1.txt")
    my_object.status()
    '''

if __name__ == '__main__':
    RAID = int(sys.argv[1])
    if(RAID == 5):
        MemoryInterface.client_stub = client_stub.client_stub()
	print("MODE: RAID 5")
    elif(RAID == 1):
        MemoryInterface.client_stub = client_stub_RAID_1.client_stub()
	print("MODE: RAID 1")
    if mode == 0:   main()
    elif mode == 1: testbench()


