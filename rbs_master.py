import socket
import os
from threading import Thread
import thread

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





Fire_Reported = 0

Fire_Event = "Event"

arrayAnimal = ["" for x in range(12)]

arrayNode = ["" for x in range(12)]

arrayTime = ["" for x in range(12)]

arrayLocation = ["" for x in range(12)]

arrayFire = ["" for x in range(12)]

#global ObjectName

ObjectName = "Start"



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
    global arrayFire
    
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
                    arrayAnimal[0] = ObjectName
                    arrayNode[0] = "Node 1 (Master Node)"
                    arrayTime[0] = now.strftime("%Y-%m-%d %H:%M:%S")

                    #arrayLocation[j] = locname.address
                    arrayLocation[0] = lattLongString                    
                    j += 1;
                    if j > 1 : 
                       j=0;
                    print(ObjectName)
                    #print("The variable, name is of type:", type(classNames[classId-1].upper()))                    


    return img,objectInfo
    



def frameCapture(clientData,a,b,c,d):

    
    #print(clientData)  
    #Fire_Reported = 0
    global Fire_Reported 
    global Fire_Event     
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
    #print(type(g.latlng))    
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
        	#Fire_Event = "FIRE"
        	arrayFire[0] = "FIRE"
        	#continue
	        print("Fire_Reported")	
        	print(Fire_Reported)
        elif int(no_red) < 29000:
	        Fire_Reported = Fire_Reported - 1
	        arrayFire[0] = str(Fire_Reported)
	        print("Fire_not Reported")	
        	print(Fire_Reported)
        	
        time.sleep(0.01)        	
        	
        cv2.imshow("Output",img)
        cv2.waitKey(1)

def cloudData(argsCloud,arg1):

    it = 0
    while True:  

       
        now = datetime.datetime.now()
        timestamp_new = now.strftime("%Y-%m-%d %H:%M:%S")
        name = "Bobby" + str(it)
        
        print(arrayFire[0])

        data = json.dumps({
	    'time_observed': arrayTime[it],
	    'location': arrayLocation[it],
	    'count': arrayNode[it],
	    'species': arrayAnimal[it],
	    'temperature': arrayFire[it],
	    'humidity':str(Fire_Reported),
	    'observer_id':name	    
	})
	
        it = it + 1
        
        if(it > 1):
           it = 0;

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
            data  = client.recv(1024)
            conv = data.decode()
            hold = conv.split('#')
            arrayAnimal[1] = hold[0]
            arrayNode[1] = hold[1]
            arrayLocation[1] = hold[2]
            arrayTime[1] = hold[3]  
            arrayFire[1] = hold[4]
            print(data)

                           
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
            


RBSReceivedTime = ""            
            
def RBSClient(y):

    #global RBSReceivedTime
    #s.bind((host,port))

    #g = geocoder.ip('me')
    #print(g.latlng)
    #geoLoc = Nominatim(user_agent="GetLoc")
    #lattlongStringArray = g.latlng
    #lattLongString = str(lattlongStringArray[0]) + "," + str(lattlongStringArray[1]) 
    i = 1

    
    try:    
        while True:
        
            now = datetime.datetime.now()
            dataString =  "$RBS" + "#" + now.strftime("%Y-%m-%d %H:%M:%S")
            
            print("Sent dataString = " + dataString)
            s.send(dataString.encode())
         
            #print (s.recv(4096))
            #data = s.recv(4096)
            #conv = data.decode()
            
            #hold = conv.split("#")
            #if(hold[0] == "$RBS"):
            #    RBSReceivedTime = hold[1]
            time.sleep(1)	             	    

    finally:
            s.close()         

def RBSClientReceive(y):

    global RBSReceivedTime
    #s.bind((host,port))

    #g = geocoder.ip('me')
    #print(g.latlng)
    #geoLoc = Nominatim(user_agent="GetLoc")
    #lattlongStringArray = g.latlng
    #lattLongString = str(lattlongStringArray[0]) + "," + str(lattlongStringArray[1]) 
    i = 1

    
    try:    
        while True:
        
            #now = datetime.datetime.now()
            #dataString =  "$RBS" + "#" + now.strftime("%Y-%m-%d %H:%M:%S")
            
            #print("RBSReceivedTime "  + RBSReceivedTime + "dataString " + dataString)
            #s.send(dataString.encode())
         
            #print (s.recv(4096))
            data = s.recv(4096)
            conv = data.decode()
            
            hold = conv.split("#")
            if(hold[0] == "$RBS"):
                RBSReceivedTime = hold[1]
            print("RBSReceivedTime = "  + RBSReceivedTime)                
            time.sleep(1)	             	    

    finally:
            s.close()         


if __name__ =="__main__":


       argsRBS = "RD"

       global s
       s = socket.socket()  
       host = socket.gethostname()        
       port = 20026
        #s.connect((host, port))
       s.connect(('192.168.39.76',port))

       y = "2"
	#t1 = threading.Thread(target=listener, args=(client,address))
	#t2 = threading.Thread(target=frameCapture, args=(argsFrame))
       t3 = threading.Thread(target=RBSClientReceive, args=(y))    
       t4 = threading.Thread(target=RBSClient, args=(y))    
	
	#t1.start()
	#t2.start()
       t3.start()
       t4.start()
	
	#t1.join()
	#t2.join()
       t3.join()
       t4.join()
       print("Done!")
