#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""

import cmd
import csv


def list_assignments(mapping):
    for name, group in mapping.items():
        if any(group):
            print(name)
            for node, pin in group.items():
                print(f"{node:>15}  →  {pin}")
            print()


# Load pin dicts
groups = ("clock", "hex", "keys", "led", "switches")
pins = dict()
for group in groups:
    pins[group] = dict()
    with open(f"{group}.csv", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if (
                len(row) == 0 or row[0].lstrip()[0] == "#"
            ):  # Skip blank lines and comments
                continue
            pins[group][row[0]] = row[1]

# Assignment command loop
class AssignLoop(cmd.Cmd):
    intro = "Pin mapper, but fast! Type help or ? to list commands.\n"
    prompt = "> "
    mapping = {group: dict() for group in groups}

    def do_list(self, _):
        """Print current assignments."""
        list_assignments(self.mapping)


if __name__ == "__main__":
    AssignLoop().cmdloop()
