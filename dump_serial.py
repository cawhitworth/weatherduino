import serial
import analysis.decode
from datetime import datetime
from VideoCapture import Device

ser = serial.Serial("COM3", 9600)

lastLong = None
lastShort = None

cam = Device()

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
                print analysis.decode.diff_bits(bits[:48], lastLong[:48])
                print analysis.decode.diff_bits(bits[48:], lastShort)

            lastLong = bits[:]
            lastShort = bits[48:]
            cam.saveSnapshot("grabs\\%s.jpg" % now)

        elif len(bits) == 32:
            print "SHORT PACKET @ %s" % now
            print display
            if lastShort != None:
                print analysis.decode.diff_bits(bits, lastShort)
            lastShort = bits[:]
            cam.saveSnapshot("grabs\\%s.jpg" % now)
        else:
            print "UNKNOWN PACKET @ %s [maybe corrupt]" % now
            print display


