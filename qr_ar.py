import cv2 as cv
import numpy as np
import sys

def read_camera_parameters(filepath='camera_parameters/intrinsic.dat'):
    inf = open(filepath, 'r')

    cmtx = []
    dist = []

    # ignore first line
    line = inf.readline()
    for _ in range(3):
        line = inf.readline().split()
        line = [float(en) for en in line]
        cmtx.append(line)

    # ignore line that says "distortion"
    line = inf.readline()
    line = inf.readline().split()
    line = [float(en) for en in line]
    dist.append(line)

    # cmtx = camera matrix, dist = distortion parameters
    return np.array(cmtx), np.array(dist)

def get_qr_coords(cmtx, dist, points):
    # Selected coordinate points for each corner of QR code.
    qr_edges = np.array([[0, 0, 0],
                         [0, 1, 0],
                         [1, 1, 0],
                         [1, 0, 0]], dtype='float32').reshape((4, 1, 3))

    # determine the orientation of QR code coordinate system with respect to camera coordinate system.
    ret, rvec, tvec = cv.solvePnP(qr_edges, points, cmtx, dist)

    # Define unit xyz axes. These are then projected to camera view using the rotation matrix and translation vector.
    unitv_points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype='float32').reshape((4, 1, 3))
    if ret:
        points, jac = cv.projectPoints(unitv_points, rvec, tvec, cmtx, dist)
        return points, rvec, tvec

    # return empty arrays if rotation and translation values not found
    else:
        return [], [], []

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

    # Converting radians to degrees
    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

def warp_qr(img, points):
    # Get QR code corners
    pts_src = points.reshape((4, 2))
    pts_dst = np.array([[0, 0], [300, 0], [300, 300], [0, 300]], dtype='float32')
    
    # Compute the perspective transform matrix
    matrix = cv.getPerspectiveTransform(pts_src, pts_dst)
    
    # Warp the perspective to get a top-down view of the QR code
    warped_img = cv.warpPerspective(img, matrix, (300, 300))
    
    return warped_img

def show_axes(cmtx, dist, in_source):
    # video를 스트리밍할 경우
    cap = cv.VideoCapture(in_source)    

    qr = cv.QRCodeDetector()

    while True:
        ret, img = cap.read()
        if ret == False: break

        ret_qr, points = qr.detect(img)

        if ret_qr:
            axis_points, rvec, tvec = get_qr_coords(cmtx, dist, points)

            # BGR color format
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]

            # check axes points are projected to camera view.
            if len(axis_points) > 0:
                axis_points = axis_points.reshape((4, 2))

                origin = (int(axis_points[0][0]), int(axis_points[0][1]))

                for p, c in zip(axis_points[1:], colors[:3]):
                    p = (int(p[0]), int(p[1]))

                    # Sometimes qr detector will make a mistake and projected point will overflow integer value. We skip these cases.
                    if origin[0] > 5 * img.shape[1] or origin[1] > 5 * img.shape[1]:
                        break
                    if p[0] > 5 * img.shape[1] or p[1] > 5 * img.shape[1]:
                        break

                    cv.line(img, origin, p, c, 5)

                # 카메라 좌표계 기준 QR 코드의 위치 정보 출력 (tvec: [x, y, z])
                print(f"QR 코드의 위치 (카메라 좌표계 기준): x={tvec[0][0]:.2f}, y={tvec[1][0]:.2f}, z={tvec[2][0]:.2f}")
                
                # 회전 벡터(rvec)를 기반으로 QR 코드의 기울기(roll, pitch, yaw) 계산
                roll, pitch, yaw = get_orientation_from_rvec(rvec)
                print(f"QR 코드 기울기 (도): roll={roll:.2f}, pitch={pitch:.2f}, yaw={yaw:.2f}")
                
                # 기울기에 따른 로봇팔 조정 방법 출력
                print("로봇팔 기울기 조정 방법:")
                if roll > 0:
                    print(f"QR 코드가 오른쪽으로 {roll:.2f}도 기울어졌습니다. 로봇팔을 왼쪽으로 기울여야 합니다.")
                elif roll < 0:
                    print(f"QR 코드가 왼쪽으로 {abs(roll):.2f}도 기울어졌습니다. 로봇팔을 오른쪽으로 기울여야 합니다.")
                
                if pitch > 0:
                    print(f"QR 코드가 앞으로 {pitch:.2f}도 기울어졌습니다. 로봇팔을 뒤로 기울여야 합니다.")
                elif pitch < 0:
                    print(f"QR 코드가 뒤로 {abs(pitch):.2f}도 기울어졌습니다. 로봇팔을 앞으로 기울여야 합니다.")
                
                if yaw > 0:
                    print(f"QR 코드가 시계 방향으로 {yaw:.2f}도 회전했습니다. 로봇팔을 반시계 방향으로 회전해야 합니다.")
                elif yaw < 0:
                    print(f"QR 코드가 반시계 방향으로 {abs(yaw):.2f}도 회전했습니다. 로봇팔을 시계 방향으로 회전해야 합니다.")

                # QR 코드의 왜곡 보정 및 이미지 저장
                warped_img = warp_qr(img, points)
                cv.imwrite('warped_qr.png', warped_img)
                print("보정된 QR 코드 이미지가 'warped_qr.png'로 저장되었습니다.")

        cv.imshow('frame', img)

        k = cv.waitKey(20)
        if k == 27: break  # 27 is ESC key.

    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    #read camera intrinsic parameters.
    cmtx, dist = read_camera_parameters()

    input_source = 'media/test_me.MOV'
    # test.mp4로 할 때 정확도가 좀 더 좋음.
    # test_me.MOV는 내 폰으로 촬영해서 올린 건데, 영상도 좀 느리고 정확도도 다소 떨어짐. frame을 너무 끊어서 그런듯?
    
    if len(sys.argv) > 1:
        input_source = int(sys.argv[1])

    show_axes(cmtx, dist, input_source)