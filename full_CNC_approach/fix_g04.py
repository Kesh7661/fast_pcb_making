import re
import sys

if len(sys.argv) != 3:
    print("Usage: fix_g04.py input.gcode output.gcode")
    sys.exit(1)

with open(sys.argv[1], 'r') as fin, open(sys.argv[2], 'w') as fout:
    for line in fin:
        match = re.match(r'(.*G04\s+P)([\d\.]+)(.*)', line)
        if match:
            seconds = float(match.group(2))
            milliseconds = int(round(seconds))
            line = f"{match.group(1)}{milliseconds}{match.group(3)}\n"
        fout.write(line)

