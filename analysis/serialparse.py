def compareBits(this, last, diffmap):
    if this == None or last == None:
        return
    for i in range(0, len(this)):
        if this[i] != last[i]:
            diffmap[i] = True

def parse(lines):
    readingPacket = False
    packet = None
    header = None

    longMap = [ False ] * 80
    shortMap = [ False ] * 32

    prevLong = None
    prevShort = None

    for line in lines:
        l = line.rstrip()
        if l.startswith("LONG PACKET") or l.startswith("SHORT PACKET"):
            header = l
            readingPacket = True
            packet = []

        if readingPacket:
            if len(l) == 0: #end of packet
                readingPacket = False
                if len(packet) not in (80, 32):
                    raise "Not a valid dump"

                if len(packet) == 80:
                    compareBits(packet, prevLong, longMap)
                    prevLong = packet[:]
                    compareBits(packet[48:], prevShort, shortMap)
                    prevShort = packet[48:]

                if len(packet) == 32:
                    compareBits(packet, prevShort, shortMap)
                    prevShort = packet[:]

            else:
                fields = l.split()
                packet += [ int(field) for field in fields if field in ("0","1") ]

    return (longMap, shortMap)

