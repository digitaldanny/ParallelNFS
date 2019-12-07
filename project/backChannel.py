'''
SUMMARY: backChannel.py
    This script instantiates n = 4->16 servers and allows the user to choose 
    which server fails.

EXAMPLE:
    python backChannel.py num_servers
'''
import xmlrpclib, config, pickle, os, sys, subprocess, time

proxy = []
num_servers   	= sys.argv[1]
num_servers   	= int(num_servers)
p               = [None for i in range(num_servers)] # subprocess handles for closing terminal windows
print("Number of servers: " + str(num_servers))
portNum 		= 8000

'''
Instantiate num_servers servers in GNOME environment. Each new server will be 
operating on portNum + i. This is how the file system will be able to specify 
which server it will communicate with.
'''
for i in range(num_servers) :
    print('running server #' + str(portNum+i))
    proxy.append(xmlrpclib.ServerProxy("http://localhost:" + str(portNum + i) + "/"))
    os.system('gnome-terminal -e \"python server.py ' + str(portNum + i) + '\"')
    #time.sleep(1)

while True:
    choice = int(raw_input("Enter 1 to corrupt server, enter 2 to corrupt block on server..."))

    if (choice != 1 and choice != 2):
        print("Valid options are 1 or 2..")
        continue

    serverNum = int(raw_input("Select Server to Corrupt..."))

    if (serverNum >= num_servers or serverNum < 0):
        print("Server number to corrupt is out of range..")
        continue

    try :
	    if(choice == 1):
		    retVal =  proxy[serverNum].corruptData()
		    print(serverNum)
		    print(pickle.loads(retVal))
	    if(choice == 2):
		    blockNum = int(raw_input("Select Block to Corrupt..."))
		    serialMessage = pickle.dumps(blockNum)
		    retVal =  proxy[serverNum].corruptDataBlock(serialMessage)
		    
		
    except Exception as err :
        print('Connection error.. closing all servers.')
        for i in range(num_servers):
            print("Killing server on port " + str(portNum + i))
            try:
                proxy[i].kill()
            except:
                pass
        break
