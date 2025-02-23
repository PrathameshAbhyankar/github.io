import socket
import os
from threading import Thread
import thread
import threading
import time
import datetime

import cv2
import numpy as np
import smtplib
#import playsound
import threading

import socket             

#from flask import Flask, render_template
#import flask
import datetime

import requests
import json

import geocoder
from geopy.geocoders import Nominatim

#global Fire_Reported

Fire_Reported = 0

arrayAnimal = ["" for x in range(12)]

arrayNode = ["" for x in range(12)]

arrayTime = ["" for x in range(12)]

arrayLocation = ["" for x in range(12)]


#global ObjectName

ObjectName = "Start"

dataString  = "Protocol"

#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "/home/pranav/Documents/RaspberryPi/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pranav/Documents/RaspberryPi/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pranav/Documents/RaspberryPi/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)




def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    j = 0
    global ObjectName 
    global array 
    global arrayAnimal
    global arrayNode
    global arrayTime
    global arrayLocation
    
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    print("Object Names : ")
                    ObjectName = str(classNames[classId-1].upper())
                    now = datetime.datetime.now()
                    dataString = ObjectName + "#Node 1 (Master Node)" + "#" + now.strftime("%Y-%m-%d %H:%M:%S")
                    #print(dataString)
                    arrayAnimal[j] = ObjectName
                    arrayNode[j] = "Node 1 (Master Node)"
                    arrayTime[j] = now.strftime("%Y-%m-%d %H:%M:%S")

                    #arrayLocation[j] = locname.address
                    arrayLocation[j] = lattLongString                    
                    j += 1;
                    if j > 10 : 
                       j=10;
                    print(ObjectName)
                    #print("The variable, name is of type:", type(classNames[classId-1].upper()))                    


    return img,objectInfo
    



def frameCapture(clientData,a,b,c,d):

    
 
    print(clientData)  
    #Fire_Reported = 0
    global Fire_Reported 
    global lattLongString
    #global dataString   
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    #cap.set(10,70)
    
    g = geocoder.ip('me')
    #print(g.latlng)
    #geoLoc = Nominatim(user_agent="GetLoc")
    lattlongStringArray = g.latlng
    lattLongString = str(lattlongStringArray[0]) + "," + str(lattlongStringArray[1]) 
    #locname = geoLoc.reverse(lattLongString)    


    while True:

        success, img = cap.read()
        result, objectInfo = getObjects(img,0.45,0.2)
        #print(objectInfo)
        blur = cv2.GaussianBlur(img, (21, 21), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)        
        lower = [18, 50, 50]
        upper = [35, 255, 255]
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        mask = cv2.inRange(hsv, lower, upper)

        output = cv2.bitwise_and(img, hsv, mask=mask)

        no_red = cv2.countNonZero(mask)

        if int(no_red) > 29000:
        	Fire_Reported = Fire_Reported + 1
        	#continue
	        print("Fire_Reported")	
        	print(Fire_Reported)
        elif int(no_red) < 29000:
	        Fire_Reported = Fire_Reported - 1
	        print("Fire_not Reported")	
        	print(Fire_Reported)
        	
        time.sleep(1)        	
        	
        cv2.imshow("Output",img)
        cv2.waitKey(1)
 
argsCloud = "CD"

def cloudData(argsCloud,arg1):

    it = 1
    while True:  

       
        now = datetime.datetime.now()
        timestamp_new = now.strftime("%Y-%m-%d %H:%M:%S")
        name = "Bobby" + str(it)
        it = it + 1    
        data = json.dumps({
	    'time_observed': arrayTime[0],
	    'location': arrayLocation[0],
	    'count': arrayNode[0],
	    'species': arrayAnimal[0],
	    'temperature': str(Fire_Reported),
	    'humidity':str(Fire_Reported),
	    'observer_id':name	    
	})

        r = requests.post('https://api.us-east.tinybird.co/v0/events', 
        params = {
	    'name': 'demo_custom_data_5038',
	    'token': 'p.eyJ1IjogImM1YmRhY2YxLTI5YzUtNDIwZS1hYzMxLTY2OWJmMjAzZjBlZCIsICJpZCI6ICIwMmFiZWM0ZC0xM2VkLTRhYzItYmE1OS1iYzQ3YTE4ZTRlZjMiLCAiaG9zdCI6ICJ1c19lYXN0In0.vuZo6A9d9-gzyqQ0ftGBeJjvyfkzwilUqsIU2T8zWYE',
	}, 
	data=data)

        print(r.status_code)
        print(r.text)
        time.sleep(1)        	


def listener(client, address):

    global ObjectName 
    print ("Accepted connection from: ", address)
    with clients_lock:
        clients.add(client)
    try:    
        while True:
            ObjectName  = client.recv(1024)
            data = ObjectName
            if not data:
                break
            else:
                print (repr(data))
                with clients_lock:
                    for c in clients:
                        c.sendall(data)
    finally:
        with clients_lock:
            clients.remove(client)
            client.close()

clients = set()
clients_lock = threading.Lock()

host = socket.gethostname()
port = 10016

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port))
s.listen(10)
th = []
i = 1;
while True:
    print ("Server is listening for connections...")
    client, address = s.accept()
    timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
    
    
    timestamp += str(i)
    client.sendall(timestamp.encode()) 
    i = i +1
    time.sleep(1)
    th.append(Thread(target=listener, args = (client,address)).start())
    
    th.append(Thread(target=frameCapture, args = (ObjectName)).start())    
    th.append(Thread(target=cloudData, args = (argsCloud)).start())        
    
#s.close()
