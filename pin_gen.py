#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""


import configparser
import re
import sys

import quartus


def is_pin_name(pin):
    match = re.fullmatch(r"PIN_[A-Z][AB]?(\d+)", pin, flags=re.IGNORECASE)
    if match:
        if 1 <= int(match.group(1)) <= 22:
            return True

    return False


def generate_bus(node, pin):
    node_bus = bus_extract(node)
    pin_bus = bus_extract(pin)
    # Node and pin both contain buses
    if node_bus is None or pin_bus is None:
        return None

    # Bus size mismatch
    node_size = abs(node_bus["start"] - node_bus["stop"]) + 1
    pin_size = abs(pin_bus["start"] - pin_bus["stop"]) + 1
    if node_size != pin_size:
        raise ValueError(f"Bus size mismatch: {node_size} vs {pin_size}")

    nodes = bus_expand(**node_bus, left="[", right="]")
    pins = bus_expand(**pin_bus)
    return zip(nodes, pins)


def bus_extract(string):
    bus_re = r"(?P<first>.*)\[ *(?P<start>\d+) *\.\. *(?P<stop>\d+) *\](?P<rest>.*)"
    parts = re.fullmatch(bus_re, string)
    if parts is None:
        return None

    start = int(parts.group("start"))
    stop = int(parts.group("stop"))

    return {"parts": parts, "start": start, "stop": stop}


def bus_expand(parts, start, stop, left="", right=""):
    template = f"{parts.group('first')}{left}{{}}{right}{parts.group('rest')}"
    return (template.format(n) for n in range_inclusive(start, stop))


def range_inclusive(start, stop):
    if start <= stop:
        return range(start, stop + 1)
    else:
        return range(start, stop - 1, -1)


# Load pin dicts
pins_cfg = configparser.ConfigParser()
pins_cfg.read("pin_map.ini")
pins = pins_cfg["pins"]

# Load mapping file
infile = sys.argv[1]
mapper = configparser.ConfigParser()
mapper.read(infile)
mapping = mapper["mapping"]

# Expand buses
for node, pin in mapping.items():
    try:
        expanded = generate_bus(node, pin)
        if expanded is not None:
            del mapping[node]
            for node_i, pin_i in expanded:
                mapping[node_i] = pin_i
    except ValueError as ve:
        print(ve)

# Handle invalid mappings and expand buses
for node, pin in mapping.items():
    pin = pin.upper()

    if pin in pins:
        mapping[node] = pins[pin]
    elif not is_pin_name(pin):
        print(f"Skipping invalid pin name: {pin}")
        del mapper["mapping"][node]

outfile = sys.argv[2]
with open(outfile, "w") as fp:
    quartus.dump(mapper["mapping"], fp)
