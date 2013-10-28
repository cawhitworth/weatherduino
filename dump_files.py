from analysis.decode import get_bits_from_file
from analysis.decode import group_bits

wireless_dumps = [
    "dumps\dump.dat", "dumps\dump2.dat", "dumps\dump3.dat", "dumps\dump4.dat",
    "dumps\dump_ss1.dat", "dumps\dump_ss2.dat", "dumps\dump_ss3.dat", "dumps\dump_ss4.dat",
    "dumps\dump_ss5.dat", "dumps\dump_ss6.dat", "dumps\dump_ss7.dat", "dumps\dump_ss8.dat"
    ]

for dump in wireless_dumps:
    print group_bits(get_bits_from_file(dump), 8)

