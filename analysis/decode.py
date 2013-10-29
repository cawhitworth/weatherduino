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

        if int(duration) > 2000 or int(duration) < 300:
            if int(tick) == 0:
                continue
            else:
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

def diff_bits(bits1, bits2, group_by = 32, subgroup_by=4):
    retVal = ""
    while len(bits1) != 0:
        b1 = []
        b2 = []
        for i in range(0, min(len(bits1), group_by)):
            b1.append( repr(bits1[i] ))
            b2.append( repr(bits2[i] ))
            if i % subgroup_by == subgroup_by - 1:
                b1.append(" | ")
                b2.append(" | ")

        d = []
        for (bit1, bit2) in zip(b1, b2):
            if bit1 == bit2:
                if bit1 == " | ":
                    d.append(" | ")
                else:
                    d.append("-")
            else:
                d.append("X")

        retVal += "".join(b1)
        retVal += "\n";
        retVal += "".join(b2)
        retVal += "\n";
        retVal += "".join(d)
        retVal += "\n";
        retVal += "\n";

        bits1 = bits1[group_by:]
        bits2 = bits2[group_by:]
    return retVal

def group_bits(bits, group_by = 16, subgroup_by = 4):
    retVal = ""
    for bit in range(0, len(bits)):
        retVal += str(bits[bit]) + " "
        if bit % group_by == group_by-1:
            retVal += "\n"
        elif bit % subgroup_by == subgroup_by-1:
            retVal += "| "

    if (len(bits)-1) % group_by != group_by-1:
        retVal += "\n"

    return retVal

def group_bits_with_vals(bits, group_by = 8):
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

