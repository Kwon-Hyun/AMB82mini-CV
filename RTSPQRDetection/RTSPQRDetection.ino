#include "StreamIO.h"
#include "VideoStream.h"
#include "RTSP.h"
#include "QRCodeScanner.h"
#include "VideoStreamOverlay.h"
#include <WiFi.h>

#define CHANNEL 0
#define KNOWN_QR_SIZE_MM 50  // 실제 QR 코드의 크기(mm 단위, 예: 50mm)
#define FOCAL_LENGTH 615.0   // 카메라의 초점 거리(픽셀 단위, 테스트 필요)

VideoSetting config(VIDEO_FHD, 30, VIDEO_H264, 0);
RTSP rtsp;
QRCodeScanner Scanner;
StreamIO videoStreamer(1, 1);
VideoStreamOverlay OSD;


// WiFi로 실시간 스트리밍 연결
char ssid[] = "LAB2M_101_5G";  // WIFI ID
char password[] = "lab2m2094";  // WIFI password
int status = WL_IDLE_STATUS;

IPAddress ip;
int rtsp_portnum;

void setup() {
    Serial.begin(115200);

    // Attempt to connect to Wifi network:
    while (status != WL_CONNECTED) {
        Serial.print("Attempting to connect to WPA SSID: ");
        Serial.println(ssid);
        status = WiFi.begin(ssid, password);

        // wait 2 seconds for connection:
        delay(2000);
    }

    ip = WiFi.localIP();
    Serial.print("Connected to WiFi. IP address: ");
    Serial.println(ip);

    config.setBitrate(2 * 1024 * 1024);
    Camera.configVideoChannel(CHANNEL, config);
    Camera.videoInit();

    rtsp.configVideo(config);
    rtsp.begin(); // 기본 port : 554
    rtsp_portnum = rtsp.getPort();

    Serial.print("RTSP stream available at rtsp://");
    Serial.print(ip);
    Serial.print(":");
    Serial.println(rtsp_portnum);

    Camera.channelBegin(CHANNEL);

    OSD.configVideo(CHANNEL, config);
    OSD.begin();

    // QR코드 Scan 시작
    Scanner.StartScanning();
}

void loop() {
    delay(1000);  // 스캔 간의 딜레이

    Scanner.GetResultString();
    Scanner.GetResultLength();

    if (Scanner.ResultString != nullptr) {
        Serial.print("QR 코드 데이터: ");
        Serial.println(Scanner.ResultString);

        // Draw OSD overlay with QR data
        //OSD.drawText(Scanner.ResultString, 100, 50, 0xFFFFFF);  // 색상 : White
    }
    
    if (Scanner.ResultLength != 0) {
        Serial.print("QR 코드 길이: ");
        Serial.println(Scanner.ResultLength);

        // QR 코드가 이미지에서 차지하는 픽셀 크기
        float qrSizeInPixels = Scanner.ResultLength; // 라이브러리 출력에 맞게 조정

        // QR 코드와 Camera 간 거리
        float distance = (KNOWN_QR_SIZE_MM * FOCAL_LENGTH) / qrSizeInPixels;
        Serial.print("QR 코드와의 예상 거리: ");
        Serial.print(distance);
        Serial.println(" mm");

        // Draw OSD overlay with QR data
        //OSD.drawText("Distance: " + String(distance) + " mm", 100, 70, 0x00FF00);  // 색상 : Green
    }
}
