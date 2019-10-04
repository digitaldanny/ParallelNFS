import InodeNumberLayer, FileNameLayer, FileSystem

FileSystem.Initialize_My_FileSystem()

'''
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
SUMMARY: test00_writeToInode
    Tests whether a message can be written to an inode and read back..

MODULES TESTED:
    InodeNumberLayer
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''
def test00_rwInode():
    
    # initialize the file system
    inodeNumberLayer = InodeNumberLayer.InodeNumberLayer
    fileNameLayer = FileNameLayer.FileNameLayer
    
    return 0

'''
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
SUMMARY: 
    main runs all the test functions listed in "testbenches" and outputs
    the pass or fail results..
+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
'''
def main():
    
    testbenches = [
        test00_rwInode
    ]
    
    messages = []
    
    # run all tests and mark when it passed or failled
    for test in testbenches:
        print "\n****************** RUNNING NEXT TEST ******************\n"
        passed = test()
        message = test.__name__ + ": "
        if passed == 0:
            message += "OK"
        else:
            message += "failed"
        messages.append(message)
        
    # after all tests have been run, output the results.
    print "\n+-----+-----+-----+-----+-----+-----+-----+-----+"
    for message in messages: print message
    print "+-----+-----+-----+-----+-----+-----+-----+-----+\n"

if __name__ == '__main__':
    main()