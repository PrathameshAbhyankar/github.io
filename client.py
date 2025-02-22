import socket
import os
import time
from threading import Thread


import socket
import time

s = socket.socket()  
host = socket.gethostname()        
port = 10016



s.connect((host, port))

i = 1

data = "time : "
while True:
    print (s.recv(4096))
    
    data += str(1)
    #s.send('Client code and Thank you for connecting'.encode())
    s.send(data.encode())
    time.sleep(1)
     
s.close() 
