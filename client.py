from Crypto.Cipher import AES
import socket
import select
import sys
import threading
import time
import pickle

def send_file(s):
	print("""Type 'stop' to cancel or enter a filename to send: """, end="")
	filename = input()
	if filename == 'stop':
		print("Exiting...")
		s.send(encrypt_msg("stop"))
		print(decrypt_msg(s.recv(4096)).decode())
	else:
		try:
			f = open(filename,'rb')
			print("File is being uploaded...")
		except FileNotFoundError:
			print("The requested file does not exist. File transfer has been terminated!")
			s.send(encrypt_msg("stop"))
			return		
		s.send(encrypt_msg(filename))

		with open(filename,'rb') as f:
			data = f.read()
			s.send(len(data).to_bytes(4,'big'))
			s.send(encrypt_msg(data))
			print("Sending...")
			time.sleep(0.7)
		f.close()
		print(decrypt_msg(s.recv(4096)).decode())

def recv_file(s):
	message = decrypt_msg(s.recv(4096)).decode()
	if message.split()[0] == "Empty":
		print("There are no uploaded files, please upload a file or wait for others to do so.")
		return
	else:
		print("\nHere are all files available for download:")
		print(message)
		print("Enter a filename to download: ", end="")
	filename = input()
	if filename == "":
		print("Not a valid file, file transfer terminated")
		return
	if filename.lower() == 'stop':
		print("Exiting...")
		s.send(encrypt_msg("stop"))
	else:
		s.send(encrypt_msg(filename))
		response = decrypt_msg(s.recv(4096)).decode()
		if response == "invalid":
			print(filename +" is not a valid file.")
			return
		remaining = int.from_bytes(s.recv(4),'big')
		f = open("client_copy_of_" + filename, 'wb')
		while remaining:
			data = s.recv(min(remaining,4096))
			remaining -= len(data)
			f.write(data)
		print("File downloaded.")
		print("File transfer has successfully terminated.")

def encrypt_msg(msg):
	obj = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
	return obj.encrypt(msg)

def decrypt_msg(msg):
	obj = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
	return obj.decrypt(msg)

HEADER_LEN = 10
IP = '127.0.0.1'
PORT = 1236

print("Please enter your name: ", end=" ")
name = input()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP, PORT))
server.send(encrypt_msg(name))

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
			message = read.recv(4096)			
			print(decrypt_msg(message).decode(), end="")
		else:
			message = sys.stdin.readline()
			if not message.split():
				continue
			server.send(encrypt_msg(message))
			sys.stdout.write("< You >")
			sys.stdout.write(message)
			sys.stdout.flush()
			if message.split()[0] == '/ft':
				send_file(server)
			elif message.split()[0] == "/rf":
				recv_file(server)
			elif message.split()[0] == "/mc":
				sys.stdout.flush()
				print(decrypt_msg(server.recv(4096)).decode())
			elif message.split()[0] == "/jc":
				sys.stdout.flush()
				print(decrypt_msg(server.recv(4096)).decode())

			

server.close()