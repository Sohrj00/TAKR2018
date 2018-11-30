import socket
import pickle
import threading
import sys
import hashlib
import os
import OpenSSL
from OpenSSL import SSL
from OpenSSL import crypto
from Crypto import Random
from Crypto.Cipher import AES
from diffiehellman.diffiehellman import DiffieHellman
from OpenCA import createCSR
class Encryptor:
    key=None
    def __init__(self, key):
        #klic musi byt v bytes
        self.key = key.encode()
    
    def pad(self, s):
        #doplni null byte(y) do pozadovane delky pro AES, musi dostat bytes
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message, key_size=256):
        #zasifruje zpravu vcetne paddingu, vraci inicializacni vektor + samotnou zasifrovanou zpravu
        key=self.key
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

   

    def decrypt(self, ciphertext):
        #desifruje zpravu a odstrani padding
        key=self.key
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")