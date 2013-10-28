import serial

ser = serial.Serial("COM3", 9600)

while True:
    message = ser.readline()
    print message,
