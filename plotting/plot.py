#!/usr/bin/env python3
"""
Plotting functions for analyses products.

File: plot.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import typing
import json
import logging
from pyneuroml.io import read_neuroml2_file
from pyneuroml.plot.PlotMorphology import plot_2D_cell_morphology
from pyneuroml.plot.PlotTimeSeries import plot_time_series_from_lems_file


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def plot_morpholgy_2d(
    cell_obj,
    highlight_spec: typing.Dict,
    filename_suffix: str,
    show_plot: bool = False,
    plane: typing.List[str] = ["xy", "yz", "zx"],
) -> None:
    """Plot the morphology of a cell

    :param neuroml_file: name of NeuroML file containing cell
    :type neuroml_file: str
    :returns: None

    """
    for p in plane:
        plot_2D_cell_morphology(
            offset=[0, 0, 0],
            cell=cell_obj,
            plane2d=p,
            save_to_file=f"{cell_obj.id}-{p}-{filename_suffix}.png",
            highlight_spec=highlight_spec,
            nogui=not show_plot,
            title=filename_suffix,
        )


if __name__ == "__main__":
    cell_obj = read_neuroml2_file("L5PC.cell.nml").cells[0]
    recorded_segments = None
    input_segments = None

    # plot morphology with segments being recorded from marked
    with open("segments_recorded.json", "r") as f:
        recorded_segments = json.load(f)

    # plot morphology with segments being input to marked
    with open("segments_poisson_inputs.json", "r") as f:
        input_segments = json.load(f)

    plot_morpholgy_2d(
        cell_obj, recorded_segments, "morphology", show_plot=True, plane=["xy"]
    )
    plot_morpholgy_2d(cell_obj, input_segments, "inputs", show_plot=True, plane=["xy"])

    colors = [val["marker_color"] for val in recorded_segments.values()]
    plot_time_series_from_lems_file(
        "LEMS_poisson_stim_sim_0.xml",
        show_plot_already=True,
        labels=False,
        colors=colors,
    )
