from Crypto.Cipher import AES
import socket
import select
import sys
import threading
import time
import pickle

def transfer_file(client_socket):
	filename = client_socket.recv(4096)
	client_socket.send("ready for file")
	file_to_send = client_socket.recv(4096)

	for c in clients:
		if c != client_socket:
			recv_call = c.send("/recv")
			c.recv(4096)
			c.send(filename)
			c.send(file_to_send)
	client_socket.send("Successfully shared file with everyone in the room")
	print("File shared")



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
local_files = {}
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
	welcome_msg = """Welcome to our chatroom! \n\n"""
	help_msg = """Here are a few things you can do: \n1) Type '/mc Edward's Chatroom to create your own chatroom called 'Edward's Chatroom' \n2) Type '/jc Stocks' to join the 'Stocks' chatroom if you know it exists\n3) Type 'Help' at anytime to see these tips again! :) \n \nYou are currently in the chatroom '{0}', you can start sending messages now! \n""".format(curr_room)
	client_socket.send(encrypt_msg(welcome_msg+help_msg))

	while True:
		try:
			#print("waiting for message")
			message = client_socket.recv(2048)
			msg = decrypt_msg(message).decode()

			if msg.split()[0] == "/mc":
				new_room = ' '.join(msg.split()[1:])
				chatrooms[new_room] = [client_socket]
				chatrooms[curr_room].remove(client_socket)
				msg = "<" + client_addr[0] + "> " + """has left chatroom '""" + str(curr_room) + """' and CREATED chatroom """ + """'""" + str(new_room) + """'!"""
				print(msg)
				curr_room = new_room
				client_socket.send(encrypt_msg("You have created & joined the room called" + """'""" + new_room + """'"""))
			elif msg.split()[0] == "/jc":
				new_room = ' '.join(msg.split()[1:])
				chatrooms[curr_room].remove(client_socket)
				chatrooms[new_room].append(client_socket)
				msg = "<" + client_addr[0] + "> " + """has left chatroom '""" + str(curr_room) + """' and JOINED chatroom """ + """'""" + str(new_room) + """'!"""
				print(msg)
				client_socket.send(encrypt_msg("""You have left chatroom '""" + str(curr_room) + """' and JOINED chatroom """ + """'""" + str(new_room) + """'!"""))								
				curr_room = new_room
			elif msg.split()[0] == "/ft":
				print("/ft command called")
				filename = client_socket.recv(4096).decode("utf-8")
				print("filename recv")
				client_socket.send("ready for file".encode("utf-8"))
				copy = "copy of " + filename
				with open(copy, 'wb') as f:
					data = client_socket.recv(4096)
					while data:
						data = client_socket.recv(4096)
						print("working...")
						f.write(data)
					print("done")
				local_files[filename] = f
				f.close()
				print("file saved")
				client_socket.send("File has been sent to server. Use /rf to retrieve")
			elif msg.split()[0] == "/rf":
				request = client_socket.recv(4096).decode("utf-8")
				client_socket.send(local_files.keys())
				filename = client_socket.recv(4096).decode("utf-8")
				file_to_send = local_files[filename] 
				client_socket.send(file_to_send)
			elif msg.split()[0].lower() == "help":
				msg = "<" + client_addr[0] + "> asked for help"
				print(msg)
				client_socket.send(encrypt_msg(help_msg))
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