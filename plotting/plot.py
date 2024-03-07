#!/usr/bin/env python3
"""
Plotting functions for analyses products.

File: plot.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import sys
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
    print(sys.argv)
    if len(sys.argv) != 2:
        print("Please provide the name of the cell file as the argument")
        sys.exit(-1)

    print(f"Working on file {sys.argv[1]}")
    cell_obj = read_neuroml2_file(sys.argv[1]).cells[0]
    recorded_segments = None
    input_segments = None
    fi_sims = None
    poisson_sims = None

    # plot morphology with segments being recorded from marked
    with open("segments_recorded.json", "r") as f:
        recorded_segments = json.load(f)
    colors = [val["marker_color"] for val in recorded_segments.values()]

    # plot morphology with segments being input to marked
    with open("segments_poisson_inputs.json", "r") as f:
        input_segments = json.load(f)

    # get fi current sims
    with open("sims_fi.json", "r") as f:
        fi_sims = json.load(f)

    # get poisson sims
    with open("sims_poisson_inputs.json", "r") as f:
        poisson_sims = json.load(f)

    plot_morpholgy_2d(
        cell_obj, recorded_segments, "morphology", show_plot=True, plane=["xy"]
    )

    for k, v in fi_sims.items():
        plot_time_series_from_lems_file(
            v["simfile"],
            show_plot_already=True,
            labels=False,
            colors=colors,
            title=f"{v['current']} nA at soma",
        )

    plot_morpholgy_2d(cell_obj, input_segments, "inputs", show_plot=True, plane=["xy"])
    for k, v in poisson_sims.items():
        plot_time_series_from_lems_file(
            v["simfile"],
            show_plot_already=True,
            labels=False,
            colors=colors,
            title="poisson spike train inputs",
        )
