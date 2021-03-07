#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""

import csv
import configparser
import sys

import quartus


# Load pin dicts
groups = ("clock", "hex", "keys", "led", "switches")
pins = dict()
for group in groups:
    with open(f"{group}.csv", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if (
                len(row) == 0 or row[0].lstrip()[0] == "#"
            ):  # Skip blank lines and comments
                continue
            pins[row[0]] = row[1]

# Load mapping file
infile = sys.argv[1]
mapper = configparser.ConfigParser()
mapper.read(infile)

outfile = sys.argv[2]
with open(outfile, "w") as fp:
    quartus.dump(mapper["mapping"], fp)
