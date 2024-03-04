#!/usr/bin/env python3
"""
Plot the morphology of a multi compartmental NeuroML cell.

File: plot_morphology.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import sys
from pyneuroml.plot.PlotMorphology import plot_2D_cell_morphology
from neuroml import Cell


def plot_morpholgy_2d(cell: Cell) -> None:
    """Plot the morphology of a cell

    :param neuroml_file: name of NeuroML file containing cell
    :type neuroml_file: str
    :returns: None

    """
    for plane in ["xy", "yz", "zx"]:
        plot_2D_cell_morphology(
            offset=[0, 0, 0],
            cell=cell,
            plane2d=plane,
            save_to_file=f"{cell.id}-{plane}.png",
        )


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: plot_morphology <NML cell file>")
        sys.exit(1)
    plot_morpholgy_2d(sys.argv[1])
