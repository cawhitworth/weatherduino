from analysis.decode import get_bits_from_file
from analysis.decode import diff_bits

bits1 = get_bits_from_file("dumps/dump_ss5.dat")
bits2 = get_bits_from_file("dumps/dump_ss7.dat")

print bits1
print bits2

print diff_bits(bits1, bits2)
