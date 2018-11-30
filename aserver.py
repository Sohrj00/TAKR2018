import socket
import pickle
import threading
import sys
import OpenSSL
from OpenSSL import crypto, SSL
from OpenCA import createCA, signReqCA
import os
from OpenCA import Utils

BUFSIZE=32768

class Server:
    connections=[]
    authenticated=[]
    sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self,addr='127.0.0.1'):
        self.sock.bind((addr,9876))
        self.sock.listen(1)
    def handler(self,c,a):
        while True:
            data=c.recv(BUFSIZE)
            if data[0:1]==b'\x15':
                print("TOHLE JE X15ka")
                print(data[1:])
                certreq= OpenSSL.crypto.load_certificate_request(crypto.FILETYPE_PEM, data[1:])
                
                with open("User.CSR.pem",'wb') as f:
                    f.write(OpenSSL.crypto.dump_certificate_request(crypto.FILETYPE_PEM, certreq))
                
                signReqCA('IntermediateAuthority','User.CSR.pem','heslo', csr_type = 'usr')
                with open('USER.cert.pem') as cert:
                    text=cert.read()
                    c.send(b'\x66'+text.encode())
                    #c.send(b'\x66'+OpenSSL.crypto.dump_certificate(crypto.FILETYPE_PEM,cert.read()))
                #c.send(b'\x20'+podepsany)
                print(Utils.verify_chain("IntermediateAuthority/certs/IntermediateAuthority.chain.pem",open('USER.cert.pem','rb').read()))
                if(Utils.verify_chain("IntermediateAuthority/certs/IntermediateAuthority.chain.pem",open('USER.cert.pem','rb').read())):
                    self.authenticated.append(c)
                    print("pridan frajer")
            elif(data[0:1]==b'\x33'):
                if(self.overitCert(data[1:])):
                    self.authenticated.append(c)
            else:
                #preposilani
                print(data)
                for connection in self.authenticated:
                    if connection is not c:
                        connection.send(data)
                if not data:
                    self.connections.remove(c)
                    if (c in self.authenticated):
                        self.authenticated.remove(c)
                    c.close()
                    break

    def overitCert(self,data):

        cert=OpenSSL.crypto.load_certificate(crypto.FILETYPE_PEM,data)
        return (Utils.verify_chain("IntermediateAuthority/certs/IntermediateAuthority.chain.pem",data))
        
    def run(self):
        while True:

            c,a = self.sock.accept()
            cThread=threading.Thread(target=self.handler,args=(c,a))
            cThread.daemon=True
            cThread.start()
            self.connections.append(c)
            print(self.connections)
            if os.path.exists('./RootCertificate') == False:
                createCA('root','RootCertificate','heslo', {'CN':'caroot.ca'})
                createCA('int', 'IntermediateAuthority', 'heslo', {'CN':'introot.CA'})
                signReqCA("RootCertificate","IntermediateAuthority",'heslo', csr_type = 'ca' )
            
                

server= Server()
server.run()