# DE0-CV pin generator

The pin planner is slow and hard to use. This script automatically
generates Quartus settings files that assign the pins from a simple
INI file.

## Example use

Input file (`input.ini`):
```ini
[mapping]
node = LEDR0
switch = PIN_AA12
display[0..6] = HEX3[0..6]

[options]
output = pins.qsf
```

Run as `python pin_gen.py input.ini`. Output file (`pins.qsf`):
```
set_location_assignment PIN_AA2 -to node
set_location_assignment PIN_AA12 -to switch
set_location_assignment PIN_Y16 -to display[0]
set_location_assignment PIN_W16 -to display[1]
set_location_assignment PIN_Y17 -to display[2]
set_location_assignment PIN_V16 -to display[3]
set_location_assignment PIN_U17 -to display[4]
set_location_assignment PIN_V18 -to display[5]
set_location_assignment PIN_V19 -to display[6]
```

## Command line syntax
```
$ python pin_gen.py --help
usage: pin_gen.py [-h] [-o OUTPUT] [-s] in_file

positional arguments:
  in_file               Input file (see below for format notes)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file. Will be clobbered if it exists. If absent, print to stdout or output specified by in_file.
  -s, --strict          Escalate warnings to errors

```

## Input file
The input file is an INI file with two sections, `mapping` and
`options`. See the [`configparser`
docs](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure)
for more information about the file format.

Pin assignments go in the `mapping` section as `node_name =
pin_name`. The pin name can be a standard names used in the DE0-CV
manual or a direct pin location. Pin names that aren't recognized are
skipped with a printed error message.

Any command line flag can alternatively be given in the `options`
section using the long name. If both are used, command line flags take
precedence. Boolean options are given as `option = True/False`.


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
