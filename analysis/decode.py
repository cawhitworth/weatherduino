import serial

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
        if line.startswith("Tick"):
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

