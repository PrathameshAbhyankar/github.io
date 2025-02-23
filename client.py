import socket
import os
import time
from threading import Thread


import socket
import time
import datetime

import geocoder
from geopy.geocoders import Nominatim

s = socket.socket()  
host = socket.gethostname()        
port = 10016



s.connect((host, port))

i = 1

data = "time : "

g = geocoder.ip('me')
    #print(g.latlng)
    #geoLoc = Nominatim(user_agent="GetLoc")
lattlongStringArray = g.latlng
lattLongString = str(lattlongStringArray[0]) + "," + str(lattlongStringArray[1]) 
    
while True:
    print (s.recv(4096))
    
    now = datetime.datetime.now()
    dataString =  "Animal" + str(i+10) + "#Node 2 (Offline Slave Node)" + "#" + lattLongString + "#" +  now.strftime("%Y-%m-%d %H:%M:%S")    
    
    #data1 = data + str(i)
    #s.send('Client code and Thank you for connecting'.encode())
    s.send(dataString.encode())
    i = i+1
    time.sleep(1)
     
s.close() 
