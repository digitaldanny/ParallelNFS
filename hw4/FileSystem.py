import time, MemoryInterface, AbsolutePathNameLayer

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
    quit()


if __name__ == '__main__':
    start = time.time()
    
    
    #DO NOT MODIFY THIS
    Initialize_My_FileSystem()
    fs = FileSystemOperations()
    #announce("INIT MEMORY")
    #fs.status()
    
    # FILE WRITE/READ TEST ----------------------------------------------------
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

