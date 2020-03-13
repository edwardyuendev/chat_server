from Crypto.Cipher import AES
import socket
import select
import sys
import threading
import time
import pickle

def send_file(s):
	print("Enter file name: ")
	filename = input()
	print("f")
	s.send(filename.encode("utf-8"))
	print("f")
	ready = s.recv(4096).decode("utf-8")
	try:
		f = open(filename,'rb')
	except FileNotFoundError:
		print("The requested file does not exist.")
	####pickle cant send files
	data = f.read(4096)
	while data:
		s.send(data)
		data = f.read(4096)
	f.close()
	print(s.recv(4096).decode("utf-8"))
	

def recv_file(s):
	print("Which file do you want to download?")
	s.send("ready for file")
	all = s.recv(4096).decode("utf-8")
	print(all)
	filename= input()
	s.send(filename)
	f = open("copy of " + filename, 'x')
	file_to_recv = s.recv(4096).decode("utf-8")
	f.write(pickle.loads(file_to_recv))
	f.close()
	print("File downloaded")

def encrypt_msg(msg):
	obj = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
	return obj.encrypt(msg)

def decrypt_msg(msg):
	obj = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
	return obj.decrypt(msg)

HEADER_LEN = 10
IP = '127.0.0.1'
PORT = 1236

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
			message = read.recv(2048)			
			print(decrypt_msg(message).decode())
		else:
			message = sys.stdin.readline()
			server.send(encrypt_msg(message))
			#sys.stdout.flush()
			sys.stdout.write("<You>")
			sys.stdout.write(message)
			sys.stdout.flush()
			if message.split()[0] == '/ft':
				send_file(server)
			if message.split()[0] == "/rf":
				recv_file(server)

			

server.close()