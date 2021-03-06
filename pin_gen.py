#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""

import csv


def list_assignments(mapping):
    for name, group in mapping.items():
        if any(group):
            print(name)
            for node, pin in group.items():
                print(f"{node:>15}  →  {pin}")
            print()


# Load pin dicts
pins = dict()
for group in ("clock", "hex", "keys", "led", "switches"):
    pins[group] = dict()
    with open(f"{group}.csv", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if (
                len(row) == 0 or row[0].lstrip()[0] == "#"
            ):  # Skip blank lines and comments
                continue
            pins[group][row[0]] = row[1]
