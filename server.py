import socket
import threading
import sys

BUFSIZE=32768

class Server:
    connections=[]
 
    sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self,addr='127.0.0.1'):
        
        self.sock.bind((addr,9876))
        self.sock.listen(1)


    def handler(self,c,a):
        while True:
            data=c.recv(BUFSIZE)
            print(data)
            for connection in self.connections:
                if connection is not c:
                    
                    connection.send(data)
            if not data:
                self.connections.remove(c)
                c.close()
                break
    def run(self):
        while True:
            c,a = self.sock.accept()
            cThread=threading.Thread(target=self.handler,args=(c,a))
            cThread.daemon=True
            cThread.start()
            self.connections.append(c)
            print(self.connections)
kek=None
if (len(sys.argv)>1):
    kek=sys.argv[1]
server= Server(kek)
server.run()