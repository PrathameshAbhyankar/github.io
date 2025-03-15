import socket
import os
import time
from threading import Thread


import _thread
import threading

import cv2
import numpy as np
import smtplib


import datetime

import geocoder
from geopy.geocoders import Nominatim

from picamera2 import Picamera2

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()


Fire_Reported = 0

arrayAnimal = ["" for x in range(12)]

arrayNode = ["" for x in range(12)]

arrayTime = ["" for x in range(12)]

arrayLocation = ["" for x in range(12)]

arrayFire = ["" for x in range(12)]


lattLongString = "location"
#global ObjectName

ObjectName = "Start"

dataString  = "Protocol"

#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "/home/pi/Documents/raspberryCamera/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Documents/raspberryCamera/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Documents/raspberryCamera/Object_Detection_Files/frozen_inference_graph.pb"

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
                    #dataString = ObjectName + "#Node 1 (Master Node)" + "#" + now.strftime("%Y-%m-%d %H:%M:%S")
                    #print(dataString)
                    arrayAnimal[0] = ObjectName
                    arrayNode[0] = "Node 2 (Offline Slave Node)"
                    arrayTime[0] = now.strftime("%Y-%m-%d %H:%M:%S")
                    #lattLongString = "19.5 , 74.3"
                    #arrayLocation[j] = locname.address
                    arrayLocation[0] = lattLongString                    
                    dataString =  arrayAnimal[0] + "#" + arrayNode[0] + "#" + arrayLocation[0] + "#" +  arrayTime[0] + "#" + arrayFire[0]
                    print(dataString)
                    #print("The variable, name is of type:", type(classNames[classId-1].upper()))                    


    return img,objectInfo
    



def frameCapture(clientData,a):

    
 
    print(clientData)  
    #Fire_Reported = 0
    global Fire_Reported 
    global lattLongString
    #global dataString   
    #cap = cv2.VideoCapture(0)
    #cap.set(3,640)
    #cap.set(4,480)
    #cap.set(10,70)
    
    g = geocoder.ip('me')
    #print(g.latlng)
    #geoLoc = Nominatim(user_agent="GetLoc")
    lattlongStringArray = g.latlng
    lattLongString = str(lattlongStringArray[0]) + "," + str(lattlongStringArray[1]) 
    #locname = geoLoc.reverse(lattLongString)    


    try:
        while True:
    


	        #success, img = cap.read()

            img = picam2.capture_array()            
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
                arrayFire[0] = "FIRE"
			#continue
                print("Fire_Reported")
                print(Fire_Reported)
		        
            elif int(no_red) < 29000:

                Fire_Reported = Fire_Reported - 1
                arrayFire[0] = str(Fire_Reported)
                print("Fire_not Reported")	
                print(Fire_Reported)
		        
            time.sleep(1)	
	        #cv2.imshow("Output",img)
            cv2.waitKey(1)
        
    except Exception as e:
     
        print("The error is: ",e)	

def listener(client, address):

    global ObjectName 
    print ("Accepted connection from: ", address)

    s = socket.socket()  
    host = socket.gethostname()        
    port = 10016
    #s.connect((host, port))
    s.connect(('192.168.39.123',port))
    #s.bind((host,port))

    #g = geocoder.ip('me')
    #print(g.latlng)
    #geoLoc = Nominatim(user_agent="GetLoc")
    #lattlongStringArray = g.latlng
    #lattLongString = str(lattlongStringArray[0]) + "," + str(lattlongStringArray[1]) 
    i = 1

    
    try:    
        while True:
            #print (s.recv(4096))	    
            #now = datetime.datetime.now()
            dataString =  arrayAnimal[0] + "#" + arrayNode[0] + "#" + arrayLocation[0] + "#" +  arrayTime[0] + "#" + arrayFire[0]
            s.send(dataString.encode())
            time.sleep(2) 
    finally:
            s.close()


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


def gyro_acc_thread(gyro,acc):

    PWR_MGMT_1   = 0x6B
    SMPLRT_DIV   = 0x19
    CONFIG       = 0x1A
    GYRO_CONFIG  = 0x1B
    INT_ENABLE   = 0x38
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    GYRO_XOUT_H  = 0x43
    GYRO_YOUT_H  = 0x45
    GYRO_ZOUT_H  = 0x47

    bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
    Device_Address = 0x68   # MPU6050 device address

    MPU_Init()

    print (" Reading Data of Gyroscope and Accelerometer")

    i = 0

    avg = 0

    begin = 0

    arrayAX = [i * 0.01 for i in range(100)]
    arrayAXString = ["" for x in range(100)]


    while True:

	#Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

	#Read Gyroscope raw value
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

	#Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0

    #Ax0 = Ax

        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0

        temp = Ax
        arrayAX[i] = Ax

     #i += 1

        if(i > 98):
             i = 0

        arrayAXString[0] = "0"
        arrayAXString[i+1] = str(Ax)

        delta = abs(float(arrayAXString[i+1]) - float(arrayAXString[i]))

        print("delta %f " %delta)

        if(delta < 0.2):
             avg = 0.5 * ( float(arrayAXString[i+1]) + float(arrayAXString[i]))
             begin = time.time()
        delta2 = abs(float(arrayAXString[i+1]) - abs(avg))
        distance = 0
        if(abs(float(arrayAXString[i+1]) > abs(avg))):
             end = time.time()
             timeCal = end - begin
             distance = 0.5 *  delta2 * ( timeCal ** 2 )
             print("avg = %f" %avg , "delta2 %f" %delta2 , "timeCal %f" %timeCal , "distance %f" %distance)


     #if(abs(arrayAX[i+1] - arrayAX[i]) < 0.3):
     #     avg = 0.5 * (arrayAX[i+1] + arrayAX[i])

     #print("i=%d" %i , "temp %.2f " %temp , "arrayAX=%.3f" %arrayAX[i] , "avg AX = %.3f" %avg)
             print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az)
             i += 1
             sleep(1)


frameArgs = "FD"
listenerArgs = "LD"  
argsGyro = "GD"

if __name__ =="__main__":



	t1 = threading.Thread(target=listener, args=(listenerArgs))
	t2 = threading.Thread(target=frameCapture, args=(frameArgs))
	t3 = threading.Thread(target=gyro_acc_thread, args=(argsGyro))    

	t1.start()
	t2.start()
	t3.start()

	t1.join()
	t2.join()
	t3.join()

	print("Done!")
