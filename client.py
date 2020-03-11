from Crypto.Cipher import AES
import socket
import select
import sys
import threading

def send_file(filename, s):
	print("Transfering " + filename + "...")
	try:
		f = open(filename,'rb')
		f.close()
	except FileNotFoundError:
		print("The requested file does not exist.")
		s.send(bytes("~error~","utf-8"))
	else:
		s.send(bytes(filename,"utf-8"))
		s.recv(1024)
		print("Uploading file to server...")
		with open(filename,'rb') as f:
			data = f.read()
			dataLen = len(data)
			s.send(dataLen.to_bytes(4,'big'))
			s.send(data)
		print(s.recv(1024).decode("utf-8"))

def recv_file(filename, s):
	print("Receiving shared group file...")
	s.send("/sendFilename") #encrpyt("/sendfile")
	filename = s.recv(1024).decode("utf-8")
	s.send("/sendFile")
	remaining = int.from_bytes(s.recv(4),'big')
	f = open(filename,"wb")
	while remaining:
		data = s.recv(min(remaining,4096))
		remaining -= len(data)
		f.write(data)
	f.close()
	print("Received file saved as",filename)

def encrypt_msg(msg):
	obj = AES.new('This is a key123'.encode('utf-8'), AES.MODE_CFB, 'This is an IV456'.encode('utf-8'))
	return obj.encrypt(msg)

def decrypt_msg(msg):
	obj = AES.new('This is a key123'.encode('utf-8'), AES.MODE_CFB, 'This is an IV456'.encode('utf-8'))
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
			print(decrypt_msg(message))
		else:
			message = sys.stdin.readline()
			server.send(encrypt_msg(message))
			#sys.stdout.flush()
			sys.stdout.write("<You>")
			sys.stdout.write(message)
			# if message == "/filetransfer"
			# 	filename = input("File name:")
			# 	message = client_socket.send(filename)
			# 	send_file(filename, server)
			sys.stdout.flush()

server.close()