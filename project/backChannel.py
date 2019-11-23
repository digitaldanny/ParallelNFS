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
    serverNum = int(raw_input("Select Server to Corrupt..."))
    try :
        retVal =  proxy[serverNum].corruptData()
        print(serverNum)
        print(pickle.loads(retVal))
        
    except Exception as err :
        print('Connection error.. closing all servers.')
        for i in range(num_servers):
            print("Killing server on port " + str(portNum + i))
            try:
                proxy[i].kill()
            except:
                pass
        break