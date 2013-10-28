import serial
import analysis.decode

ser = serial.Serial("COM3", 9600)

while True:
    message = ser.readline().rstrip()
    if message == "START":
        packet = []
        while True:
            line = ser.readline().rstrip()
            if line != "END":
                packet.append(line)
            else:
                break
        try:
            bits = analysis.decode.get_bits(packet)
            print "PACKET"
            analysis.decode.group_bits(bits)
        except:
            print "INVALID PACKET"
