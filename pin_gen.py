#!/usr/bin/env python3

"""
Generate a Quartus settings file to map FPGA pins for the Altera DE0-CV.
"""

import cmd
import csv
import os

import quartus


def yn(prompt):
    """Prompt a yes/no question, default no. Return True for yes."""
    yn = input(f"{prompt} [y/N]? ")
    return len(yn) > 0 and yn[0].lower() == "y"


def yesno(prompt):
    """Prompt a yes/no question with strict input."""
    yn = None
    while yn != "yes" and yn != "no":
        if yn is not None:
            print("Please enter yes or no.")
        yn = input(f"{prompt} [yes/no]? ").lower()

    return yn == "yes"


def pick_one(options, prompt, help=None, help_char="?"):
    """
    Pick exactly one from several single-character options, with
    optional help string.
    """
    if help is not None:
        if help_char in options:
            raise ValueError(f"{help_char} is both help and option")
        options += help_char

    full_prompt = f"{prompt} [{options}]: "
    while True:
        choice = input(full_prompt)
        if len(choice) == 0:
            continue
        choice = choice[0].lower()

        if help is not None and choice == help_char:
            print(help)
        elif choice in options:
            return choice


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

    def assignment_for(self, node):
        for group in self.mapping.values():
            if node in group:
                return group[node]

    def do_list(self, _):
        """Print current assignments."""
        self.list_assignments()

    def do_map(self, arg):
        """Map a node to an FPGA pin."""
        args = arg.split()
        if len(args) == 0:
            node, group, pin = self.interactive_map()
            if node is None:
                return
        elif len(args) == 2:
            node, pin = args
            for group in self.groups:
                if pin in pins[group]:
                    group = group
                    break
            else:
                if yn(f"{pin} is not a recognized pin name. Continue"):
                    group = "other"
                else:
                    return
        else:
            print(f"Error: expected 0 or 2 arguments, got {len(args)}.")
            return

        self.mapping[group][node] = pin

    def interactive_map(self):
        node = input("Node: ")

        pre_assignment = self.assignment_for(node)
        if pre_assignment is not None:
            if not yn(f"{node} is already assigned to {pre_assignment}. Overwrite"):
                return None, None, None

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

        return node, group, pin

    def do_quit(self, _):
        """Save pin assignments and quit."""
        file = quartus.pick_qsf("Save mappings")
        if file == "":
            return
        if os.path.exists(file):
            mode = pick_one("awc", "File exists ", help="Append, overWrite, or Cancel")
            if mode == "c":
                return
        else:
            mode = "w"

        with open(file, mode) as fp:
            quartus.dump(self.mapping, fp)

        return True


if __name__ == "__main__":
    AssignLoop(groups).cmdloop()
