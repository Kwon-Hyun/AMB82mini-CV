import cv2 as cv
import numpy as np
import sys
from enum import IntEnum


#! 1. 카메라 외부 환경 요소 전처리
#! 2. 전처리된 환경에서 QR만 인식
#! 3. 인식한 QR decoding
#! 4. QR algorithm에서 position pattern, alignment pattern에 대해 분석
#! 5. QR 기울기, 위치 파악 (grid도 활용)
#! 6. 어떻게 조정해야 좋은지 출력


# 1-1 이미지 전처리
def img_preprocess(img):
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_blur = cv.GaussianBlur(img_gray, (5, 5), 0)
    _, thresh = cv.threshold(img_blur, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    img_edge = cv.Canny(thresh, 50, 150)

    return img_edge

    




# 4-1 그리드 그리기
def draw_grid(frame):
    height, width = frame.shape[:2] 

    # 세로선
    cv.line
    # 가로선

