import os
from Crypto.Cipher import AES
import socket
import select
import sys
import threading

def encrypt_message(message):
	#modify to always work even with non-16 length stuff
	message = message + (16 - (len(message) % 16)) * chr(16 - len(message) % 16)
	encryptor = AES.new(key)
	text = encryptor.encrypt(message)
	return text

def decrypt_message(text):
	decryptor = AES.new(key)
	message = decryptor.decrypt(text)
	message = message[: (-1 * ord(message[len(message)-1]))]
	return message

keyfile = 'readme.txt'
key = ""
try:
	file = open(keyfile, "rb")
	key = file.readline()
	file.close()
except:
	print("keyfile generated")
	key = os.urandom(16)
	file = open(keyfile, "wb")
	file.write(key)
	file.close()

message = 'hello there bitch'
obj = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
enc = obj.encrypt(message)
print('encrypted message: ', enc)
obj2 = AES.new('This is a key123', AES.MODE_CFB, 'This is an IV456')
dec = obj2.decrypt(enc)
print('decrypted message: ', dec.decode())