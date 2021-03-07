#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""

import cmd
import csv


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

    def __init__(self, groups, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = groups
        self.mapping = {group: dict() for group in self.groups}
        self.mapping["other"] = dict()

    def choose_group(self):
        letters = {g[0]: g for g in self.groups}
        letters_help = "".join(letters.keys())
        while True:
            group = input(f"Group [{letters_help}o?]: ")[0].lower()
            if group == "?":
                print(
                    """Enter the first letter of a pin group. Groups are:
 clock:    50MHz built-in clock
 hex:      7-segment displays (common anode)
 keys:     pushbuttons (active low)
 led:      red LEDs (active high)
 switches: slide switches
 other:    pins without special support"""
                )
            elif group == "o":
                return "other"
            elif group in letters:
                return letters[group]

    def list_assignments(self):
        for name, group in self.mapping.items():
            if any(group):
                print(name)
                for node, pin in group.items():
                    print(f"{node:>15}  →  {pin}")
                print()

    def do_list(self, _):
        """Print current assignments."""
        self.list_assignments()

    def do_map(self, arg):
        """Map a node to an FPGA pin."""
        args = arg.split()
        if len(args) == 0:
            node = input("Node: ")
            group = self.choose_group()
            pin = None
            if group != "other":
                while pin not in pins[group]:
                    pin = input("Pin [?]: ")
                    if pin == "?":
                        print(f"Pins in {group}: {', '.join(pins[group].keys())}")
            else:
                while pin is None:
                    pin = input("Pin [?]: ")
                    if pin == "?":
                        print(
                            "Any pin number on the FPGA (caution: not checked for validity)"
                        )
                        pin = None

            self.mapping[group][node] = pin


if __name__ == "__main__":
    AssignLoop(groups).cmdloop()
