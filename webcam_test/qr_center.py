import cv2 as cv
import numpy as np
import sys

from enum import IntEnum


# QR 코드 위치를 나타내는 열거형
class Position(IntEnum):
    TopLeft = 0
    MidLeft = 1
    BottomLeft = 2
    TopMid = 10
    Mid = 11
    BottomMid = 12
    TopRight = 20
    MidRight = 21
    BottomRight = 22


# 카메라 파라미터 파일에서 intrinsic 및 distortion 매개변수 읽기
def read_camera_parameters(filepath='camera_parameters/intrinsic.dat'):
    inf = open(filepath, 'r')

    cmtx = []
    dist = []

    # 첫 번째 줄 무시
    line = inf.readline()
    for _ in range(3):
        line = inf.readline().split()
        line = [float(en) for en in line]
        cmtx.append(line)

    # "distortion"이라는 줄 무시
    line = inf.readline()
    line = inf.readline().split()
    line = [float(en) for en in line]
    dist.append(line)

    # cmtx = 카메라 매트릭스, dist = 왜곡 파라미터
    return np.array(cmtx), np.array(dist)


# 이미지 전처리 (외부 환경 처리를 위해)
def preprocess_img(img):
    # 1. 그레이스케일 변환
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # 2. 블러링 (Gaussian 블러링으로 노이즈 제거)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
    # 3. 이진화 (Thresholding)
    _, binary = cv.threshold(blurred, 100, 255, cv.THRESH_BINARY)
    
    # 4. 에지 검출 (Canny Edge Detection)
    edges = cv.Canny(binary, 50, 150)
    
    return edges


# QR 코드 좌표를 기반으로 회전 및 이동 벡터 계산
def get_qr_cords(cmtx, dist, points):
    qr_edges = np.array([[0, 0, 0],
                         [0, 1, 0],
                         [1, 1, 0],
                         [1, 0, 0]], dtype='float32').reshape((4, 1, 3))

    ret, rvec, tvec = cv.solvePnP(qr_edges, points, cmtx, dist)

    unitv_points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype='float32').reshape((4, 1, 3))
    if ret:
        points, jac = cv.projectPoints(unitv_points, rvec, tvec, cmtx, dist)
        return points, rvec, tvec
    else:
        return [], [], []


# 회전 벡터를 기반으로 회전 각도 계산
def get_orientation_from_rvec(rvec):
    rotation_matrix, _ = cv.Rodrigues(rvec)
    sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
    
    singular = sy < 1e-6
    if not singular:
        roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        pitch = np.arctan2(-rotation_matrix[2, 0], sy)
        yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        roll = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        pitch = np.arctan2(-rotation_matrix[2, 0], sy)
        yaw = 0

    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)


# 프레임에 텍스트 출력
def framePrint(frame, text: str, position: Position = Position.BottomLeft, padPx=10):
    font = cv.FONT_HERSHEY_SIMPLEX
    textSize = cv.getTextSize(text, font, fontScale=1.0, thickness=1)[0]
    frameW = frame.shape[1]
    frameH = frame.shape[0]

    yPos = int(position) % 10
    if yPos == 0: # Y Top
        y = textSize[1] + padPx
    elif yPos == 1: # Y Mid
        y = int(frameH / 2) + int(textSize[1] / 2)
    else:  # yPos == 2. Y Bottom
        y = frameH - padPx

    xPos = int(position) // 10
    if xPos == 0: # X Left
        x = padPx
    elif xPos == 1:  # X Mid
        x = int(frameW / 2) - int(textSize[0] / 2)
    else:  # xPos == 2  # X Right
        x = frameW - textSize[0] - padPx

    cv.putText(frame, text, (x, y), font, fontScale=1.0, color=(255, 255, 255))


# 화면을 3x3 그리드로 나누는 함수
def draw_grid(frame):
    height, width = frame.shape[:2]
    
    # 세로선 (3등분)
    cv.line(frame, (width//3, 0), (width//3, height), (255, 255, 255), 2)
    cv.line(frame, (2*width//3, 0), (2*width//3, height), (255, 255, 255), 2)
    
    # 가로선 (3등분)
    cv.line(frame, (0, height//3), (width, height//3), (255, 255, 255), 2)
    cv.line(frame, (0, 2*height//3), (width, 2*height//3), (255, 255, 255), 2)


# QR 코드 중심이 화면에서 어느 쪽으로 치우쳐 있는지 판단하고 출력
def check_qr_shift(points, width, height):
    center_x = np.mean(points[:, :, 0])
    center_y = np.mean(points[:, :, 1])

    # 좌우 치우침 판단
    if center_x < width // 3:
        x_shift = "왼쪽"
    elif center_x > 2 * width // 3:
        x_shift = "오른쪽"
    else:
        x_shift = "중앙"

    # 상하 치우침 판단
    if center_y < height // 3:
        y_shift = "위쪽"
    elif center_y > 2 * height // 3:
        y_shift = "아래쪽"
    else:
        y_shift = "중앙"

    return x_shift, y_shift


# 카메라 좌표계에서 QR 코드의 위치와 화면 내 치우침을 동시에 출력
def show_axes_with_position(cmtx, dist, camera_id=0):
    cap = cv.VideoCapture(camera_id)
    qr = cv.QRCodeDetector()

    while True:
        ret, img = cap.read()
        if not ret: break

        height, width = img.shape[:2]

        # 이미지 전처리
        preprocessed_img = preprocess_img(img)  # 전처리된 이미지 할당

        # 그리드 그리기
        draw_grid(img)

        # QR 코드 감지 (전처리된 이미지 사용)
        ret_qr, points = qr.detect(preprocessed_img)

        # QR code가 decoding됐는지 확인
        if ret_qr:
            axis_points, rvec, tvec = get_qr_cords(cmtx, dist, points)

            if len(axis_points) > 0:
                axis_points = axis_points.reshape((4, 2))
                origin = (int(axis_points[0][0]), int(axis_points[0][1]))

                colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]

                for p, c in zip(axis_points[1:], colors[:3]):
                    p = (int(p[0]), int(p[1]))
                    if origin[0] > 5 * width or origin[1] > 5 * height:
                        break
                    if p[0] > 5 * width or p[1] > 5 * height:
                        break
                    cv.line(img, origin, p, c, 5)

                # QR 코드의 위치와 화면 치우침 정보 계산
                x_shift, y_shift = check_qr_shift(points, width, height)
                roll, pitch, yaw = get_orientation_from_rvec(rvec)

                # 카메라 좌표계에서 QR 코드의 3D 위치 출력 (x, y, z)
                x, y, z = tvec[0][0], tvec[1][0], tvec[2][0]
                print(f"QR 코드 위치 (카메라 좌표계): x={x:.2f}, y={y:.2f}, z={z:.2f}")
                print(f"QR 코드 치우침: {x_shift}, {y_shift}")
                print(f"QR 코드 기울기 (도): roll={roll:.2f}, pitch={pitch:.2f}, yaw={yaw:.2f}")

                # 화면에 출력할 텍스트
                position_text = f"QR 좌표: x={x:.2f}, y={y:.2f}, z={z:.2f}"
                shift_text = f"QR 치우침: {x_shift}, {y_shift}"

                # 화면에 좌표와 치우침 정보 표시
                framePrint(img, position_text, Position.TopLeft)
                framePrint(img, shift_text, Position.BottomLeft)
        #else:
        #    print("QR code 인식 완료. decoding 실패..")

        # 이미지 출력
        cv.imshow('Camera with QR and Grid', img)
        cv.imshow('Preprocessed Image', preprocessed_img)  # 전처리된 이미지 출력

        if cv.waitKey(20) == 27:  # 'ESC' 키로 종료
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    # 카메라 매개변수 읽기
    cmtx, dist = read_camera_parameters()

    # 카메라로 QR 코드 감지 및 좌표, 치우침 정보 표시
    camera_id = 0  # AMB82 Mini 보드 카메라 ID로 설정
    show_axes_with_position(cmtx, dist, camera_id)