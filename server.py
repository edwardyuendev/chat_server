import socket
import select
import sys
import threading

HEADER_LEN = 10
IP = '127.0.0.1'
PORT = 1235

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
				client_socket.send(msg)

			except:
				client_socket.close()
				clients.remove(client_socket)

def receive_msg(client_socket, client_addr):
	client_socket.send("Welcome to our chatroom! Enjoy chatting!".encode())
	while True:
		try:
			#print("waiting for message")
			message = client_socket.recv(2048).decode()
			if message:
				msg = "<" + client_addr[0] + ">" + message
				print("Received message from " + msg)
				broadcast_global(msg.encode(), client_socket)
			else:
				clients.remove(client_socket)

		except:
			continue

while True:
	client_socket, client_addr = server.accept()
	clients.append(client_socket)
	print(client_addr[0] + "connected")
	thread = threading.Thread(target=receive_msg, args=(client_socket, client_addr))
	thread.start()
	#thread.start_new_thread(receive_msg, (client_socket, client_addr))

server_socket.close()
