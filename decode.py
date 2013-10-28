
def closest_to(candidates, value):
    delta = abs(candidates[0] - value)
    retVal = candidates[0]
    for index in range(1, len(candidates)):
        thisDelta = abs(candidates[index] - value)
        if thisDelta < delta:
            delta = thisDelta
            retVal = candidates[index]
    return retVal

wireless_dumps = ["dump.dat", "dump2.dat", "dump3.dat", "dump4.dat"]

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

def get_bits(filename):
    expect = LineLevel.NONE

    bits = []

    with open(filename, "r") as f:
        for line in f:
            if line.startswith("Tick"):
                continue

            s = line.split()

            if len(s) != 2:
                continue

            (tick, duration) = s

            if int(duration) > 2000:
                continue

            width = closest_to(pulse_widths, int(duration))

            level = LineLevel.from_width(int(duration))

            if expect != LineLevel.NONE:
                if expect != level:
                    print "Out of sync"

            if level == LineLevel.HIGH:
                expect = LineLevel.LOW
                if width == 1500:
                    bits.append(1)
                else:
                    bits.append(0)
            elif level == LineLevel.LOW:
                expect = LineLevel.HIGH

    return bits

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

for dump in wireless_dumps:
    print group_bits(get_bits(dump), 8)
