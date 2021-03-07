#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""


import configparser
import sys

import quartus


# Load pin dicts
pins = configparser.ConfigParser().read("pin_map.ini")
pins = pins["pins"]

# Load mapping file
infile = sys.argv[1]
mapper = configparser.ConfigParser()
mapper.read(infile)

outfile = sys.argv[2]
with open(outfile, "w") as fp:
    quartus.dump(mapper["mapping"], fp)
