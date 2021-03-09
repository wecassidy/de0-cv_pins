# DE0-CV pin generator

The pin planner is slow and hard to use. This script automatically
generates Quartus settings files that assign the pins from a simple
INI file.

## Example
Step 0: clone the repository

Suppose you want to make a 4-bit register on the DE0-CV in a Quartus
project named "register". The project has three inputs named D (a
four-line bus), CLK, and RST. There is one output Q, another 4-line
bus. Planned connections:
* D → SW0 through SW3
* CLK → KEY0
* RST → KEY1
* Q → LEDR0 through LEDR3

First write a file describing the mappings, named `pins.ini` (or
whatever you want, the file name doesn't matter):
```ini
[mapping]
D[0..3] = SW[0..3]
CLK = KEY0
RST = KEY1
Q[0..3] = LEDR[0..3]
```

The file is in INI format. The first line starts a section named
`mapping`, and each line after that has the format `node name = pin
assignment`. Notice how the D and Q buses are assigned; `D[0..3] =
SW[0..3]` is equivalent to
```ini
D[0] = SW0
D[1] = SW1
D[2] = SW2
D[3] = SW3
```

Next, use the script to generate a Quartus settings file containing
the pin assignments: on the command line, run `python3
/path/to/script/pin_gen.py /path/to/pins.ini -o output.qsf`. This will
generate a file named `output.qsf` containing the following:
```
set_location_assignment PIN_U7 -to CLK
set_location_assignment PIN_W9 -to RST
set_location_assignment PIN_U13 -to D[0]
set_location_assignment PIN_V13 -to D[1]
set_location_assignment PIN_T13 -to D[2]
set_location_assignment PIN_T12 -to D[3]
set_location_assignment PIN_AA2 -to Q[0]
set_location_assignment PIN_AA1 -to Q[1]
set_location_assignment PIN_W2 -to Q[2]
set_location_assignment PIN_Y3 -to Q[3]
```

Make sure `output.qsf` is in the project folder. Finally, add the line
`source output.qsf` to the project's settings file (`register.qsf`) so
that Quartus will use the generated pin assignments. I recommend
deleting existing `set_location_assignment` lines in the project's
`qsf` file to avoid accidental conflicts, then never touching the Pin
Planner again.

## Command line syntax
```
$ python pin_gen.py --help
usage: pin_gen.py [-h] [-o OUTPUT] [-s | --strict | --no-strict] [-f | --force | --no-force]
                  in_file

positional arguments:
  in_file               Input file (see below for format notes)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file. Will be clobbered if it exists. If absent, print to
                        stdout or output specified by in_file.
  -s, --strict, --no-strict
                        Escalate warnings to errors
  -f, --force, --no-force
                        Don't ask before overwriting existing files
```

## Input file
The input file is an INI file with two sections, `mapping` (mandatory)
and `options` (optional). See the [`configparser`
docs](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure)
for more information about the file format.

Pin assignments go in the `mapping` section as `node_name =
pin_name`. The pin name can be a standard names used in the DE0-CV
manual or a direct pin location. Pin names that aren't recognized are
skipped with a printed error message.

Any command line flag can alternatively be given in the `options`
section using the long name. If both are used, command line flags take
precedence. Boolean options are given as `option = True/False` and
default to False unless otherwise specified.


## Buses

Buses, written like `abc[start..stop]def`, are expanded to a series of
individual pin assignments. If the node and pin buses have different
sizes, the assignment is skipped with a printed error message.

Start and stop must both be non-negative integers. The range is
inclusive; if `stop` is greater than `start` then the assignment
counts down.

Node buses are expanded *with* the square brackets (to match Quartus'
convention) but pin buses are expanded *without* the square brackets
(to match the DE0-CV pin names). For example, `number[0..2] = SW[2..0]`
will be expanded to:

    number[0] = SW2
    number[1] = SW1
    number[2] = SW0

If expanding a pin bus leads to some valid pins and some invalid pins,
the valid pins are kept.
