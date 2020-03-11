from Crypto.Cipher import AES
import socket
import select
import sys
import threading
import requests
import string
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup

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
	obj = AES.new('This is a key123'.encode('utf-8'), AES.MODE_CFB, 'This is an IV456'.encode('utf-8'))
	return obj.encrypt(msg.encode('utf-8'))

def decrypt_msg(msg):
	obj = AES.new('This is a key123'.encode('utf-8'), AES.MODE_CFB, 'This is an IV456'.encode('utf-8'))
	return obj.decrypt(msg.encode('utf-8'))

def chatbot(question):
	answer = ''
	text = ''
	results = list(search(question, tld="co.in", num=10, stop=3, pause=1))
	soup = BeautifulSoup((requests.get(results[0])).content, features="lxml")
	for a in soup.findAll('p'):
		text += '\n' + ''.join(a.findAll(text = True))
	text = text.replace('\n', '')
	text = text.split('.')
	answer = (text[0].split('?')[0]).translate({ord(c): None for c in string.whitespace}) #https://www.journaldev.com/23763/python-remove-spaces-from-string
	if len(answer) > 0:
		return answer
	else:
		return "I do not know. Ask me something else please."

HEADER_LEN = 10
IP = '127.0.0.1'
PORT = 1236

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((IP, PORT))
server.listen()
print("Chat server is now listening: ")

clients = []

def broadcast_global(msg, conn):
	for client_socket in clients:
		if client_socket != conn:
			try:
				client_socket.send(encrypt_msg(msg))

			except:
				client_socket.close()
				clients.remove(client_socket)

def receive_msg(client_socket, client_addr):
	welcome_msg = "Welcome to our chatroom! Enjoy chatting!"
	client_socket.send(encrypt_msg(welcome_msg))

	while True:
		try:
			#print("waiting for message")
			message = client_socket.recv(2048)
			msg = decrypt_msg(message).decode()

			if len(msg) > 0:
				msg = "<" + client_addr[0] + ">" + msg
				print("Received message from " + msg)
				broadcast_global(msg, client_socket)
			else:
				clients.remove(client_socket)

		except:
			continue

		# if msg == "/filetransfer":
		# 	message = client_socket.recv(2048)
		# 	recv_file(filename, client_socket)
		# 	for c in clients
		# 		send_file(filename, c)



while True:
	client_socket, client_addr = server.accept()
	clients.append(client_socket)
	print(client_addr[0] + " has connected!")
	thread = threading.Thread(target=receive_msg, args=(client_socket, client_addr))
	thread.start()
	#thread.start_new_thread(receive_msg, (client_socket, client_addr))

server_socket.close()
