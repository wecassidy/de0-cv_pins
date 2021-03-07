"""
Functions to handle interacting with Quartus projects
"""

map_template = "set_location_assignment {pin} -to {node}"


def dumps(mapping):
    return (
        "\n".join(
            map_template.format(pin=pin, node=node) for node, pin in mapping.items()
        )
        + "\n"
    )


def dump(mapping, fp):
    """Save the mapping to a qsf file (given an opened file)."""
    fp.write(dumps(mapping))
