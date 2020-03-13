from Crypto.Cipher import AES
import socket
import select
import sys
import threading

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
files_per_room = { 'Global' : {} }

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
				files_per_room[str(curr_room)] = {}
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
				if filename == "no":
					client_socket.send("/ft exited".encode("utf-8"))
				else:
					print("filename recv")
					client_socket.send("ready for file".encode("utf-8"))
					copy = "copy of " + filename
					remaining = int.from_bytes(client_socket.recv(4),'big')
					f = open(copy,"wb")
					while remaining:
						data = client_socket.recv(min(remaining,4096))
						remaining -= len(data)
						f.write(data)
					files_per_room[str(curr_room)][filename] = f
					f.close()
					print("File " + filename + " saved")
					client_socket.send("File has been sent to server. Use /rf to retrieve".encode("utf-8"))
			elif msg.split()[0] == "/rf":
				print("/rf protocol started")
				request = client_socket.recv(4096).decode("utf-8")
				print(not bool(files_per_room[str(curr_room)]))
				if not files_per_room[str(curr_room)]:
					client_socket.send("No files. Press enter to exit".encode("utf-8"))
				else:
					client_socket.send(str(files_per_room[str(curr_room)].keys()).encode("utf-8"))
				filename = client_socket.recv(4096).decode("utf-8")
				if filename != "no": 
					file_to_send = files_per_room[str(curr_room)][filename]
					with open("copy of " + filename,'rb') as f:
						data = f.read()
						dataLen = len(data)
						client_socket.send(dataLen.to_bytes(4,'big'))
						client_socket.send(data)
						print("Sending...")
					f.close()
					print("File transfered")
				print("/rf protocol terminated")
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