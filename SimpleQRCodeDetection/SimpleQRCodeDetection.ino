#include "VideoStream.h"
#include "QRCodeScanner.h"

#define CHANNEL 0
#define KNOWN_QR_SIZE_MM 50  // 실제 QR 코드의 크기(mm 단위, 예: 50mm)
#define FOCAL_LENGTH 615.0   // 카메라의 초점 거리(픽셀 단위, 테스트 필요)

VideoSetting config(CHANNEL);
QRCodeScanner Scanner;

void setup() {
    Serial.begin(115200);
    Camera.configVideoChannel(CHANNEL, config);
    Camera.videoInit();
    Scanner.StartScanning();
}

void loop() {
    delay(1000);  // 스캔 간의 딜레이
    Scanner.GetResultString();
    Scanner.GetResultLength();
    
    if (Scanner.ResultString != nullptr) {
        Serial.print("QR 코드 데이터: ");
        Serial.println(Scanner.ResultString);
    }
    
    if (Scanner.ResultLength != 0) {
        Serial.print("QR 코드 길이: ");
        Serial.println(Scanner.ResultLength);

        // QR 코드가 이미지에서 차지하는 픽셀 크기
        float qrSizeInPixels = Scanner.ResultLength; // 라이브러리 출력에 맞게 조정
        float distance = (KNOWN_QR_SIZE_MM * FOCAL_LENGTH) / qrSizeInPixels;

        Serial.print("QR 코드와의 예상 거리: ");
        Serial.print(distance);
        Serial.println(" mm");
    }
}