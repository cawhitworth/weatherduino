import sys
import serial
import analysis.decode
from datetime import datetime

ser = serial.Serial("COM3", 9600)

cam = None
if len(sys.argv) == 2:
    if sys.argv[1] == "-c":
        from VideoCapture import Device
        cam = Device()
        print "Capturing webcam grabs"

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
            display = analysis.decode.group_bits(bits)
        except:
            print "INVALID PACKET @ %s" % now
            continue

        if len(bits) == 80:
            print "LONG PACKET @ %s" % now
            print display
            if lastLong != None:
                print
                print "DIFF"
                print analysis.decode.diff_bits(bits[:48], lastLong[:48])
                print analysis.decode.diff_bits(bits[48:], lastShort)

            lastLong = bits[:]
            lastShort = bits[48:]
            if cam != None:
                cam.saveSnapshot("grabs\\%s.jpg" % now)

        elif len(bits) == 32:
            print "SHORT PACKET @ %s" % now
            print display
            if lastShort != None:
                print
                print "DIFF"
                print analysis.decode.diff_bits(bits, lastShort)
            lastShort = bits[:]
            if cam != None:
                cam.saveSnapshot("grabs\\%s.jpg" % now)
        else:
            print "UNKNOWN PACKET @ %s [maybe corrupt]" % now
            print display


