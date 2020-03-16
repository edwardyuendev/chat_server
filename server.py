from Crypto.Cipher import AES
import socket
import select
import sys
import threading
import time
from bs4 import BeautifulSoup
import requests
import string
from googlesearch import search
from lxml import html

def chatbot(question):
	text = ''
	results = list(search(question, tld="com", num=1, stop=1, pause=1))
	bs = BeautifulSoup((requests.get(results[0])).content, features="lxml").findAll('p')
	for a in bs:
		text += '\n' + ''.join(a.findAll(text = True))
	text = text.replace('\n', '')
	line = text.split('.')
	answer = line[0].split('?')[0] 
	parse = answer.translate({ord(c): None for c in string.whitespace}) #https://www.journaldev.com/23763/python-remove-spaces-from-string
	answer += "\n"
	if len(parse) > 0:
		return answer
	else:
		return "Error, cannot query. Try something else."

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
	#request_name = "Please enter your name: "
	#client_socket.send(encrypt_msg(request_name))
	name = decrypt_msg(client_socket.recv(4096)).decode()	
	welcome_msg = "Hi " + name +  """! Welcome to our chatroom! \n\n"""
	help_msg = """Here are a few things you can do: \n1) Type '/mc abc' to create & join your own chatroom named 'abc'. \n2) Type '/jc efg' to join the 'efg' chatroom if you know it exists.\n3) Type 'chatrooms' to see all available chatrooms to join.\n4) Type '/ft' to initiate a file transfer to the server.\n5) Type '/rf' to download a file from the server\n6) Type '/google Who is Kevin Durant?' to ask Google who Kevin Durant is! \n7) Type 'help' at anytime to see these tips again! :) \n \nYou are currently in the chatroom '{0}', you can start sending messages now! \n""".format(curr_room)
	time.sleep(0.5)
	client_socket.send(encrypt_msg(welcome_msg+help_msg))

	while True:
		help_msg = """Here are a few things you can do: \n1) Type '/mc abc' to create & join your own chatroom named 'abc'. \n2) Type '/jc efg' to join the 'efg' chatroom if you know it exists.\n3) Type 'chatrooms' to see all available chatrooms to join.\n4) Type 'help' at anytime to see these tips again! :) \n \nYou are currently in the chatroom '{0}', you can start sending messages now! \n""".format(curr_room)		
		try:
			message = client_socket.recv(4096)
			msg = decrypt_msg(message).decode()

			if msg.split()[0] == "/mc":
				new_room = ' '.join(msg.split()[1:])
				chatrooms[new_room] = [client_socket]
				chatrooms[curr_room].remove(client_socket)
				msg = "< " + name + " > " + """has left chatroom '""" + str(curr_room) + """' and CREATED chatroom """ + """'""" + str(new_room) + """'!"""
				print(msg)
				curr_room = new_room
				files_per_room[str(curr_room)] = {}
				client_socket.send(encrypt_msg("You have created & joined the room called " + """'""" + new_room + """'"""))
			elif msg.split()[0] == "/jc":
				new_room = ' '.join(msg.split()[1:])
				if new_room not in chatrooms:
					client_socket.send(encrypt_msg(new_room + " is not a valid chatroom. Type 'chatrooms' to see all available chatrooms or create a new one!"))
					print("< " + name + " > failed to join a chatroom")
					continue
				chatrooms[curr_room].remove(client_socket)
				chatrooms[new_room].append(client_socket)
				msg = "< " + name + " > " + """has left chatroom '""" + str(curr_room) + """' and JOINED chatroom """ + """'""" + str(new_room) + """'!"""
				print(msg)
				client_socket.send(encrypt_msg("""You have left chatroom '""" + str(curr_room) + """' and JOINED chatroom """ + """'""" + str(new_room) + """'!"""))								
				curr_room = new_room
			elif msg.split()[0] == "chatrooms":
				response = "\nHere are all of the chatrooms that you can join:\n"
				for key in chatrooms.keys():
					response += key
					response += "\n"
				response += """\nType '/jc hij' to join the chatroom called 'hij'.\n"""
				client_socket.send(encrypt_msg(response))
			elif msg.split()[0] == "files":
				response = "\nHere are all of the files that you can download:\n"
				for key in files_per_room[curr_room].keys():
					response += key
					response += "\n"
				response += "\n"
				client_socket.send(encrypt_msg(response))
			elif msg.split()[0] == "/ft":
				msg = "<" + name + "> has initiated file transfer."
				print(msg)
				filename = decrypt_msg(client_socket.recv(4096)).decode()
				if filename == "stop":
					msg = "<" + name + "> has stopped file transfer."
					print(msg)
					client_socket.send(encrypt_msg("File transfer has halted."))
				else:
					copy = "server_copy_of_" + filename
					remaining = int.from_bytes(client_socket.recv(4),'big')
					print("filename received")
					f = open(copy,"wb")
					while remaining:
						data = decrypt_msg(client_socket.recv(min(remaining,4096)))
						remaining -= len(data)
						f.write(data)
					files_per_room[str(curr_room)][filename] = f
					f.close()
					print("File " + filename + " saved")
					response = """The file '""" + filename + """' has been succesfully uploaded to the server! \nUse /rf to download any files from the server!"""
					client_socket.send(encrypt_msg(response))
			elif msg.split()[0] == "/rf":
				print("/rf protocol started")
				if not files_per_room[str(curr_room)]:
					print("No rooms in this server")
					client_socket.send(encrypt_msg("Empty"))
					continue
				else:
					response = ""
					for key in files_per_room[curr_room].keys():
						response += key
						response += "\n"
					client_socket.send(encrypt_msg(response))
				filename = decrypt_msg(client_socket.recv(4096)).decode()
				if filename not in files_per_room[str(curr_room)]:
					print(name + " requested to download an invalid file")
					client_socket.send(encrypt_msg("invalid"))
					continue
				client_socket.send(encrypt_msg("valid"))
				print("Sending file with filename: ", filename)
				if filename != "stop": 
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
				msg = "< " + name + " > asked for help"
				print(msg)
				client_socket.send(encrypt_msg("\n"+help_msg))
			elif msg.split()[0].lower() == "/google":
				print(name + " initiated a google search.")
				query = ' '.join(msg.split()[1:])
				client_socket.send(encrypt_msg("Searching now...\n"))
				time.sleep(.5)
				client_socket.send(encrypt_msg("Google: " + chatbot(query)))
				print("google search complete")				
			elif len(msg) > 0:
				msg = "< " + name + " > " + msg
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