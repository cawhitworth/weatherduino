def closest_to(candidates, value):
    delta = abs(candidates[0] - value)
    retVal = candidates[0]
    for index in range(1, len(candidates)):
        thisDelta = abs(candidates[index] - value)
        if thisDelta < delta:
            delta = thisDelta
            retVal = candidates[index]
    return retVal


pulse_widths = [ 500, 1000, 1500 ]

class LineLevel:
    NONE = 1
    HIGH = 2
    LOW = 3

    @classmethod
    def from_width(cls, w):
        if closest_to(pulse_widths, w) == 1000:
            return cls.LOW
        else:
            return cls.HIGH

def get_bits_from_file(filename):
    with open(filename, "r") as f:
        return get_bits(f)

def get_bits(lines):
    expect = LineLevel.NONE

    bits = []

    for line in lines:
        line = line.rstrip()

        if line.startswith("Tick"):
            continue

        if len(line) == 0:
            continue

        s = line.split()

        if len(s) != 2:
            raise "Invalid data"

        (tick, duration) = s

        if int(duration) > 2000 or int(duration) < 400:
            raise "Invalid data"

        width = closest_to(pulse_widths, int(duration))

        level = LineLevel.from_width(int(duration))

        if expect != LineLevel.NONE:
            if expect != level:
                raise "Out of sync"

        if level == LineLevel.HIGH:
            expect = LineLevel.LOW
            if width == 1500:
                bits.append(1)
            else:
                bits.append(0)
        elif level == LineLevel.LOW:
            expect = LineLevel.HIGH

    return bits

def diff_bits(bits1, bits2, group_by = 32):
    while len(bits1) != 0:
        b1 = [repr(x) for x in bits1[0:group_by-1]]
        b2 = [repr(x) for x in bits2[0:group_by-1]]
        d = [ "-" if bit1 == bit2 else "X" for (bit1,bit2) in zip(b1,b2) ]
        print "".join(b1)
        print "".join(b2)
        print "".join(d)
        print

        bits1 = bits1[group_by:]
        bits2 = bits2[group_by:]


def group_bits(bits, group_by):
    index = 0
    val = 0
    for bit in range(0, len(bits)):
        print bits[bit],
        val += bits[bit] << (index % group_by)
        index += 1
        if index == group_by:
            print val
            val = 0
            index = 0

