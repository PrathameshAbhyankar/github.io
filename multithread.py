import cv2
import numpy as np
import smtplib
#import playsound
import threading

from flask import Flask, render_template
#import flask
import datetime

#global Fire_Reported

Fire_Reported = 0

arrayAnimal = ["" for x in range(12)]

arrayNode = ["" for x in range(12)]

arrayTime = ["" for x in range(12)]


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


app = Flask(__name__)    

@app.route("/")
def function1():

   print("Function 1 running")
   global Fire_Reported
   #function2()
   now = datetime.datetime.now()
   #timeString = now.strftime("%Y-%m-%d %H:%M:%S")
   timeString = "Fire no. :" + str(Fire_Reported)
   #hold = ObjectName.split('#')
   #ObjectNameLocal = hold[0]
   #node = hold[1]
   #timeString = hold[2]
   
   #print("Full string")
   print(ObjectName)



   templateData = {
      'title' : 'HELLO!',
      'time': arrayTime[0] ,
      'entity': arrayAnimal[0],
      'node':arrayNode[0],
      'time1': arrayTime[1] ,
      'entity1': arrayAnimal[1],
      'node1':arrayNode[1],      
      'time2': arrayTime[2] ,
      'entity2': arrayAnimal[2],
      'node2':arrayNode[2],      
      'time3': arrayTime[3] ,
      'entity3': arrayAnimal[3],
      'node3':arrayNode[3],      
      'time4': arrayTime[4] ,
      'entity4': arrayAnimal[4],
      'node4':arrayNode[4] ,     
      'time5': arrayTime[5] ,
      'entity5': arrayAnimal[5],
      'node5':arrayNode[5]  ,    
      'time6': arrayTime[6] ,
      'entity6': arrayAnimal[6],
      'node6':arrayNode[6]   ,   
      'time7': arrayTime[7] ,
      'entity7': arrayAnimal[7],
      'node7':arrayNode[7]    ,  
      'time8': arrayTime[8] ,
      'entity8': arrayAnimal[8],
      'node8':arrayNode[8]     , 
      'time9': arrayTime[8] ,
      'entity9': arrayAnimal[9],
      'node9':arrayNode[9]      ,
      'time10': arrayTime[10] ,
      'entity10': arrayAnimal[10],
      'node10':arrayNode[10]       
      }
   return render_template('webdata.html', **templateData)  
   #return 0


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    j = 0
    global ObjectName 
    global array 
    
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
                    j += 1;
                    if j > 10 : 
                       j=10;
                    print(ObjectName)
                    #print("The variable, name is of type:", type(classNames[classId-1].upper()))                    


    return img,objectInfo
    


@app.route('/<string:page_name>')
def index2(page_name):
    print(f"{page_name}")
    #print()  
    #Fire_Reported = 0
    global Fire_Reported 
    #global dataString   
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    #cap.set(10,70)
    



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
        	
        cv2.imshow("Output",img)
        

        cv2.waitKey(1)



if __name__ == "__main__":


    app.run(host='192.168.236.123', port=5000, debug=True)       


    
        
