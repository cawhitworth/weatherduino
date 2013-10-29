import sys
from analysis.serialparse import parse

def prettyprint(bitmap):
    for i in range(0, len(bitmap)):
        if longMap[i]:
            print "X",
        else:
            print "-",

        if i % 4 == 3:
            print " ",

        if i % 16 == 15:
            print


with open(sys.argv[1], "r") as f:
    (longMap, shortMap) = parse(f)

    print "Long diffs:"
    prettyprint(longMap)

    print "Short diffs:"
    prettyprint(shortMap)
