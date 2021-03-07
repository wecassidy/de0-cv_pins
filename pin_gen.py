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


def choose_group(groups):
    letters = {g[0]: g for g in groups}
    letters_help = "".join(letters.keys())
    while True:
        group = input(f"Group [{letters_help}?]: ")[0].lower()
        if group == "?":
            print(
                """Enter the first letter of a pin group. Groups are:
 clock:    50MHz built-in clock
 hex:      7-segment displays (common anode)
 keys:     pushbuttons (active low)
 led:      red LEDs (active high)
 switches: slide switches
 other:    pins without special support """
            )
        elif group in letters:
            return letters[group]


# Load pin dicts
groups = ("clock", "hex", "keys", "led", "switches", "other")
pins = dict()
for group in groups:
    if group == "other":  # Other group is for unsupported names
        continue

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

    def do_map(self, arg):
        """Map a node to an FPGA pin."""
        args = arg.split()
        if len(args) == 0:
            node = input("Node: ")
            group = choose_group(groups)
            pin = None
            while pin not in pins[group]:
                pin = input("Pin [?]: ")
                if pin == "?":
                    print(f"Pins in {group}: {', '.join(pins[group].keys())}")

            self.mapping[group][node] = pin


if __name__ == "__main__":
    AssignLoop().cmdloop()
