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
			quit()


	''' WRITE CODE HERE '''


