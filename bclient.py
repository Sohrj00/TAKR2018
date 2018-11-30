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
import Encryptor
import time
BUFSIZE=32768

class Client:
    sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mujAES=None 
    cli=None
    def __init__(self,adress):
        self.sock.connect((adress, 9876))
        if os.path.isfile('User.private.pem') == False:
            createCSR('User','heslo',{'CN':'USER_FQDN'})
            self.poslatCertReq()
            print("ZADAM SI CERTIFIKAT")
        elif os.path.isfile('USER.cert.pem') == False:
                #self.vyzadatCert()
                self.poslatCertReq()
                print("zadam o certifikat kvuli USER.cert.pem")
        else:
            print("NACITAM ZE SLOZKY JAK BOSSs")
            self.cert=OpenSSL.crypto.load_certificate(crypto.FILETYPE_PEM,open('USER.cert.pem').read())
            self.poslatCert()
        
        
        
        self.cli=DiffieHellman()
        self.cli.generate_public_key()
        #presunout do runu
        self.vyzadatKlic()
        
      
        iThread=threading.Thread(target=self.sendMessage)
        iThread.daemon=True
        iThread.start()
        self.run()


    def run(self):
        
        while True:
            data=self.sock.recv(BUFSIZE)
            #misto na hrani si s daty
            if not data:
                #ukonceni komunikace
                break
            elif data[0:1]==b"\x11":
                #kdyz prijde ridici znak x11-posleme na vyzadani klic
                self.poslatKlic()
            elif data[0:1]==b"\x12":
                #kdyz prijde ridici znak x12 tak si nastavime klic ktery nasleduje po tomto bytu
                self.nastavitKlic(data[1:])
                
            elif data[0:1]==b"\x13":
                #nezasifrovana komunikace
                print(data.decode())
                #vynuceni DH pokud prijde nezasifrovana zprava
                #self.sock.send(b'\x11')
            elif data[0:1]==b"\x14":
                #nastaveni klice v pripade ze byl vyzadan nebo tak neco
                self.jinenastaveniklice(data[1:])
            elif data[0:1]==b'\x20':
                self.nastavitCert(data[1:])
            else:
                #vychozi stav- prijdou data bez ridiciho znaku-> predpokladame ze jsou zasifrovana AESem podle dohodnuteho hesla
                data=self.mujAES.decrypt(data)
                print(data.decode())
    def vyzadatCert(self):
        self.sock.send(b'\x65')
    def nastavitCert(self,data):
        #self.cert=OpenSSL.crypto.load_certificate_request(crypto.FILETYPE_PEM, data)
        self.cert=OpenSSL.crypto.load_certificate(crypto.FILETYPE_ASN1,data)
    def poslatCert(self):
        text=OpenSSL.crypto.dump_certificate(crypto.FILETYPE_PEM,self.cert)
        self.sock.send(b'\x33'+text)
    def poslatCertReq(self):
        #posle certifikat na podepsani
        cert = open('User.CSR.pem')
        certificate = OpenSSL.crypto.load_certificate_request(crypto.FILETYPE_PEM, open('User.CSR.pem').read())
        certext = OpenSSL.crypto.dump_certificate_request(crypto.FILETYPE_PEM, certificate)
        print(certext)
        
        self.sock.send(b'\x15'+certext)
        cert.close()
    def poslatKlic(self):
        #posle ridici znak nasledovany klicem
        self.sock.send(b'\x12'+str(self.cli.public_key).encode())
    def jinenastaveniklice(self,data):
        #dela zajimave veci, ale jen v urcitem pripade
        self.cli.generate_shared_secret(int(data.decode()),echo_return_key=True)
        superklic=str(self.cli.shared_secret)
        xy=hashlib.sha256(superklic.encode()).hexdigest()[:32]
        print("2222222222222222222222222222")
        print(xy)
        self.mujAES=Encryptor.Encryptor(xy)

    def nastavitKlic(self,data):
        #nastavuje klic na zaklade dat ktere dostane
        self.cli.generate_shared_secret(int(data.decode()),echo_return_key=True)
        superklic=str(self.cli.shared_secret)
        xy=hashlib.sha256(superklic.encode()).hexdigest()[:32]
        print("111111111111111111111")
        print(xy)
        self.mujAES=Encryptor.Encryptor(xy)
        self.sock.send(b'\x14'+str(self.cli.public_key).encode())
    def vyzadatKlic(self):
        #nemam klic ale chci, poslu ridici znak 
        self.sock.send(b'\x11')
    def sendMessage(self):
        #hlavni chatova smycka
        
        while True:
            msg=str(input(""))
            
            if self.mujAES is not None:
                msg=self.mujAES.encrypt(msg.encode())
                self.sock.send(msg)
            else:
                msg=msg.encode()
                self.sock.send(b'\x13'+msg)
    

kek='127.0.0.1'
client=Client(kek)