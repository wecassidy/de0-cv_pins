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


def pick_qsf(prompt=""):
    """
    Pick a qsf save file. Uses a Qt GUI window if available, otherwise
    a (bad) text interface.
    """
    try:
        from PyQt5.QtWidgets import QApplication, QFileDialog

        app = QApplication([])
        return QFileDialog.getSaveFileName(
            parent=None, caption=prompt, filter="Quartus settings file (*.qsf)"
        )[0]
    except ImportError:
        filename = input(f"{prompt}: ")
        return filename
