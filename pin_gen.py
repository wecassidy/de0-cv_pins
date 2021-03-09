#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""

import argparse
import configparser
import os
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


def warn(message, strict, *args, **kwargs):
    print(message, *args, file=sys.stderr, **kwargs)
    if strict:
        sys.exit(1)


def yn(prompt):
    """Prompt a yes/no question, default no. Return True for yes."""
    yn = input(f"{prompt} [y/N]? ")
    return len(yn) > 0 and yn[0].lower() == "y"


# Switch working dir to script location to load pin map
cwd = os.getcwd()
script_cwd = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_cwd)

# Load pin dicts
pins_cfg = configparser.ConfigParser()
pins_cfg.read("pin_map.ini")
pins = pins_cfg["pins"]

# Switch back to original working directory
os.chdir(cwd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example input file:

    [mapping]
    node = LEDR0
    switch = PIN_AA12
    display[0..6] = HEX3[0..6]

    [options]
    output = pins.qsf

Pin assignments go in the "mapping" section as node_name =
pin_name. The pin name can be a standard names used in the DE0-CV
manual or a direct pin location. Pin names that aren't recognized are
skipped with a printed error message.

Any command line flag can alternatively be given in the "options"
section using the long name. If both are used, command line flags take
precedence. Boolean options are given as option = True/False.


Buses
-----

Buses, written like abc[start..stop]def, are expanded to a series of
individual pin assignments. If the node and pin buses have different
sizes, the assignment is skipped with a printed error message.

Start and stop must both be non-negative integers. The range is
inclusive; if stop > start then the assignment counts down.

Node buses are expanded WITH the square brackets (to match Quartus'
convention) but pin buses are expanded WITHOUT the square brackets (to
match the DE0-CV pin names). For example, number[0..2] = SW[2..0] will
be expanded to:

    number[0] = SW2
    number[1] = SW1
    number[2] = SW0

If expanding a pin bus leads to some valid pins and some invalid pins,
the valid pins are kept.

""",
    )
    parser.add_argument("in_file", help="Input file (see below for format notes)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file. Will be clobbered if it exists. If absent, print to stdout "
        "or output specified by in_file.",
    )
    parser.add_argument(
        "-s", "--strict", action="store_true", help="Escalate warnings to errors"
    )
    args = parser.parse_args()

    # Load mapping file
    mapper = configparser.ConfigParser()
    mapper.optionxform = lambda x: x
    mapper.read(args.in_file)
    mapping = mapper["mapping"]
    strict = args.strict or mapper.getboolean("options", "strict", fallback=False)

    # Expand buses
    for node, pin in mapping.items():
        try:
            expanded = generate_bus(node, pin)
            if expanded is not None:
                del mapping[node]
                for node_i, pin_i in expanded:
                    mapping[node_i] = pin_i
        except ValueError as ve:
            warn(ve, strict)

    # Handle invalid mappings and expand buses
    for node, pin in mapping.items():
        pin = pin.upper()

        if pin in pins:
            mapping[node] = pins[pin]
        elif not is_pin_name(pin):
            warn(f"Skipping invalid pin name: {pin}", strict)
            del mapping[node]

    out_file = mapper.get("options", "output", fallback=None)
    out_file = args.output if args.output else out_file
    if out_file is not None:
        overwrite = True
        if os.path.exists(out_file):
            overwrite = yn(f"{out_file} exists. Continue")
        if overwrite:
            with open(out_file, "w") as fp:
                quartus.dump(mapping, fp)
    else:
        print(quartus.dumps(mapping))
