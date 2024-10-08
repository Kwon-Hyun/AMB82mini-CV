import cv2
import os
import math
import numpy
import scipy

vc = cv2.VideoCapture(0)
if vc.isOpened():
    rval, frame = vc.read()
else:   
    rval = False

while rval:
    rval, frame = vc.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 120, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 1, math.pi/1, 1, None, 23, 1)    #20-25 works well 

    if lines != None:       
        for line in lines[0]:
            pt1 = (line[0],line[1])
            pt2 = (line[2],line[3])
            cv2.line(frame, pt1, pt2, (0,0,255), 2)

    cv2.imshow("edge", frame)
    ch = cv2.waitKey(50)

    if ch != -1:
        print ("kepressed")
        print (ch)
        break
    cv2.destroyAllWindows()