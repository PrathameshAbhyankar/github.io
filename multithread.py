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

#global ObjectName

ObjectName = "Start"

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
   templateData = {
      'title' : 'HELLO!',
      'time': timeString ,
      'entity': ObjectName
      }
   return render_template('webdata.html', **templateData)  
   #return 0


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    global ObjectName
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
                    print(classNames[classId-1].upper())
                    print("The variable, name is of type:", type(classNames[classId-1].upper()))                    


    return img,objectInfo
    


@app.route('/<string:page_name>')
def index2(page_name):
    print(f"{page_name}")
    #print()  
    #Fire_Reported = 0
    global Fire_Reported    
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


    app.run(host='192.168.145.123', port=5000, debug=True)       


    
        
