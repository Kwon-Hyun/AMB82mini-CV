# OHT에서 사물 탐지
# 1. QR을 detection하고, 해당 marker가 QR이라는 인지 파악
# 2. 인지했다면, OHT를 느리게 움직이도록 조정 (사진 촬영을 위해)
# 3. 촬영한 사진에서 QR의 position, alignment pattern을 분석해 왜곡 보정

import cv2 as cv
import numpy as np

import time


#! Level 1 : QR detection -> QR 인지 -> OHT 느리게 움직이도록 조정

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

detector = cv.QRCodeDetector()

while cap.isOpened():

    success, img = cap.read()
    
    start = time.perf_counter()

    value, points, qrcode = detector.detectAndDecode(img)


    if value != "":

        x1 = points[0][0][0]
        y1 = points[0][0][1]
        x2 = points[0][2][0]
        y2 = points[0][2][1]

        x_center = (x2-x1) / 2 + x1
        y_center = (y2-y1) / 2 + y1

        cv.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255))

        cv.circle(img, (int(x_center), int(y_center)), ())
        
    