import socket
import select
import sys
import threading

HEADER_LEN = 10
IP = '127.0.0.1'
PORT = 1235

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP, PORT))

while True:
	sockets_list = [sys.stdin, server]
	# Calls Unix select() system call or Windows select() WinSock call with three parameters:
	#   - rlist - sockets to be monitored for incoming data
	#   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
	#   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
	# Returns lists:
	#   - reading - sockets we received some data on (that way we don't have to check sockets manually)
	#   - writing - sockets ready for data to be send thru them
	#   - errors  - sockets with some exceptions
	# This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
	read_sockets, write_sockets, exception_sockets = select.select(sockets_list, [], sockets_list)
	for read in read_sockets:
		if read == server:
			message = read.recv(2048).decode()
			print(message)
		else:
			message = sys.stdin.readline()
			server.send(message.encode())
			#sys.stdout.flush()
			sys.stdout.write("<You>")
			sys.stdout.write(message)
			sys.stdout.flush()

server.close()