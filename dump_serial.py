import sys
import serial
import analysis.decode
from datetime import datetime

ser = serial.Serial("COM3", 9600)

lastLong = None
lastShort = None

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
        now = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

        try:
            bits = analysis.decode.get_bits(packet)
            print "VALID PACKET @ %s" % now
        except:
            print "INVALID PACKET @ %s" % now

        print len(packet)
        print packet

