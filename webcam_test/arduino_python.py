import serial
import time

arduino = serial.Serial('/dev/cu.usbserial-1430', 115200)
time.sleep(1)

print("1을 입력하면 LED ON, 0을 입력하면 LED OFF")

while True:
    var = input("숫자 입력 (1 또는 0)")
    
    if (var == '1'):
        var = var.encode('utf-8')

        arduino.write(var)
        print("LED ON")

        time.sleep(1)
    
    if (var == '0'):
        var = var.endode('utf-8')

        arduino.write(var)
        print("LED OFF")

        time.sleep(1)