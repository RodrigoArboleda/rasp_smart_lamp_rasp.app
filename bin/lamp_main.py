import threading
import time
from bluetooth import *
import select

USER_MAX_CONNECT = 5

TIME_VF_THREAD = 5

TIME_OUT_SOCK = 7200

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "LampRasp",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
                    )

class connection_bluetooth(threading.Thread):
		
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
		super(connection_bluetooth,self).__init__(group=group, target=target, name=name, verbose=verbose)
		
		self.client_sock = args

	def run(self):

		if self.client_sock != None:

			self.client_sock.setblocking(0)

			while True:
				data = ""
				try:
					ready = select.select([self.client_sock], [], [], TIME_OUT_SOCK)
					if ready[0]:
						data = self.client_sock.recv(10)

					if len(data) == 0:
						self.client_sock.close()
						print("Thread finished")	
						break

					if data == 'quit000000':
						self.client_sock.close()
						print("Thread finished")
						break
					
					else:
						print ("received [%s]" % data)


				except IOError:
					self.client_sock.close()
					print("Thread finished")
					break

				except KeyboardInterrupt:
					self.client_sock.close()
					print("Thread finished")
					break
		
		else:
			print("Client socket problem")



def main():
	
	thread_list = []
	sock_client_list = []
	try:
		while True:  

			print ("Waiting for connection on RFCOMM channel %d" % port)

			client_sock, client_info = server_sock.accept()
			t = connection_bluetooth(args=(client_sock))
			t.start()

			print ("Accepted connection from ", client_info)

			thread_list.append(t)
			sock_client_list.append(client_sock)

			for i in thread_list:
				if not(i.is_alive()):
					index = thread_list.index(i)
					thread_list.remove(i)
					del sock_client_list[index]
					

			while len(thread_list) >= USER_MAX_CONNECT:
				print ("Waiting for a connection to finish")
				for i in thread_list:
					if not(i.is_alive()):
						index = thread_list.index(i)
						thread_list.remove(i)
						del sock_client_list[index]
				time.sleep(TIME_VF_THREAD)

	except KeyboardInterrupt:
		
		for i in thread_list:
			if not(i.is_alive()):
				index = thread_list.index(i)
				thread_list.remove(i)
				del sock_client_list[index]

		for i in sock_client_list:
			i.close()
		server_sock.close()

if __name__ == '__main__':
    main()