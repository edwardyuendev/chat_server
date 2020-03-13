from Crypto.Cipher import AES
import socket
import select
import sys
import threading

def send_file(filename, s):
	try:
		f = open(filename,'rb')
		f.close()
	except FileNotFoundError:
		print("The requested file does not exist.")

	#for user in client:
	with open(str(filename), 'rb') as sendingFile:
		packet = sendingFile.read(1024)
		while (packet):
			s.send(packet) #user.send(packet)
			packet = f.read(1024)

def recv_file(filename, s):
	with open(str(filename), 'wb') as f:
		while True:
			packet = s.recv(1024)
			while (packet):
				f.write(data)

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
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((IP, PORT))
server.listen()
print("Chat server is now listening: ")

clients = []
chatrooms = {'Global':[]}

def broadcast_global(msg, conn):
	for client_socket in clients:
		if client_socket != conn:
			try:
				client_socket.send(encrypt_msg(msg))

			except:
				client_socket.close()
				clients.remove(client_socket)

def broadcast_to_room(msg, conn, room_name):
	for client_socket in chatrooms[room_name]:
		if client_socket != conn:
			try:
				client_socket.send(encrypt_msg(msg))

			except:
				client_socket.close()
				clients.remove(client_socket)
				chatrooms[room_name].remove(client_socket)

def receive_msg(client_socket, client_addr):
	chatrooms['Global'].append((client_socket))
	curr_room = 'Global'
	welcome_msg = """Welcome to our chatroom! Enjoy chatting! You're in chatroom "Global"! """
	client_socket.send(encrypt_msg(welcome_msg))

	while True:
		try:
			#print("waiting for message")
			message = client_socket.recv(2048)
			msg = decrypt_msg(message).decode()

			if msg.split()[0] == "/mc":
				new_room = ' '.join(msg.split()[1:])
				chatrooms[new_room] = [client_socket]
				chatrooms[curr_room].remove(client_socket)
				msg = "<" + client_addr[0] + "> " + """has left chatroom '""" + str(curr_room) + """' and joined chatroom """ + """'""" + str(new_room) + """'!"""
				print(msg)
				curr_room = new_room
				client_socket.send(encrypt_msg("You have created & joined the room called" + """'""" + new_room + """'"""))
			elif len(msg) > 0:
				msg = "<" + client_addr[0] + ">" + msg
				print("Received message from " + msg)
				broadcast_to_room(msg, client_socket, curr_room)
			else:
				clients.remove(client_socket)

		except:
			continue

while True:
	client_socket, client_addr = server.accept()
	clients.append(client_socket)
	print(client_addr[0] + " has connected!")
	thread = threading.Thread(target=receive_msg, args=(client_socket, client_addr))
	thread.start()
	#thread.start_new_thread(receive_msg, (client_socket, client_addr))

server_socket.close()