import time, MemoryInterface, AbsolutePathNameLayer

'''
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
CONFIGURATIONS
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
mode -  0: command line mode for final project
        1: testbench mode
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''
mode    = 0

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
    def status(self):
        print(MemoryInterface.status())

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
                # EXIT: Terminate program.
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
                offset = response[2]
                length = response[3]
                ret = fs.read(filename, offset, length)
                print(ret)
                
            elif cmd == WRITE:
                # WRITE: Write a string (packed between quotations)
                filename = response[1]
                msg = response[2]
                offset = response[3]
                fs.write('/A/B/file.txt', msg, offset)
                
            elif cmd == STATUS:
                fs.status()
                
            elif cmd == RM:
                print('rm')
                
            else:
                location = response[1]
                fs.rm(location)
            
        except Exception:
            print("Command (" + str(cmd) + ") not recognized..")

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
    
    ret = fs.read('/A/B/file.txt', 0, 12)
    if ret == -1: endit()
    
    #fs.status()
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
    if mode == 0:   main()
    elif mode == 1: testbench()


