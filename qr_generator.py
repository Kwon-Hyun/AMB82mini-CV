import qrcode
from PIL import Image

# QR 코드에 포함할 좌표 정보
data = "240923_QR_test"

# 지정된 크기의 QR 코드 생성
qr = qrcode.QRCode(
    version=1,  # QR 코드의 크기를 제어
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,  # 각 박스의 픽셀 크기
    border=4,  # 테두리 두께(박스 단위)
)

qr.add_data(data)
qr.make(fit=True)

# QR 코드 이미지 생성
qr_img = qr.make_image(fill='black', back_color='white')

# 고정된 크기 (예: 200x200 픽셀)로 이미지 크기 조정
qr_img = qr_img.resize((300, 300), Image.ANTIALIAS)

# QR 코드 이미지 저장
qr_img.save("qr_demo2.png")

# QR 코드 크기를 출력 (출력 시 해상도에 따라 다름)
print("QR 코드 크기: 300 x 300 pixel")