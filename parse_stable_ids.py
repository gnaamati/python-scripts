import sys
import re

filename = sys.argv[1]
print (filename)

f = open(filename)
for line in f:
    line = line.rstrip('\n')
    #print(line)
    r1 = re.findall(r"'(.*)'", line)
    stable_id = r1[0]
    print(f'id=stable_id')

