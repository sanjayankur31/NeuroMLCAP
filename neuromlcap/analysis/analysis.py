#!/usr/bin/env python3
"""
Main runner script for the NeuroML Cell Analysis Pipeline (NeuroMLCAP)

File: analysis.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import json
import logging
import os
import random
import shutil

import neuroml
import neuroml.utils as nmlu
import numpy
from matplotlib.pyplot import cm
from pyneuroml.io import read_neuroml2_file, write_neuroml2_file
from pyneuroml.lems.LEMSSimulation import LEMSSimulation
from pyneuroml.utils.units import convert_to_units
from pyneuroml.runners import (
    run_multiple_lems_with,
    execute_command_in_dir,
    execute_multiple_in_dir,
)
from pyneuroml.plot.PlotTimeSeries import plot_time_series_from_lems_file

from ..plot.plot import plot_morphology_2d
from ..config.config import read_config
from ..utils.utils import create_analysis_dir

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NeuroMLCAP(object):
    """Main class for NeuroMLCAP"""

    recorded_segments_file = "segments_recorded.json"
    fi_sims_file = "sims_fi.json"
    poisson_input_sims_file = "sims_poisson_inputs.json"
    poisson_input_segments_file = "segments_poisson_inputs.json"

    def __init__(self, config_file_name):
        """Initialise"""
        self.cfg_file_name = config_file_name
        self.cfg = None
        self.nml_doc = None
        self.cell = None
        self.analyses_dir = None
        self.model_files = None
        # TODO: formalise recorders by creating recording classes with well
        # defined attributes instead of using generic dicts: will make it
        # easier to code/extend/access
        self.recorder = {}
        self.unbranched_segment_groups = None
        self.recorded_segments = {}

    def prepare(self, folder):
        """Prep for analyses

        :param folder: name of folder, if none given, create a new one
        :type folder: str

        :returns: name of analysis folder
        :rtype: str
        """
        self.cfg = read_config(self.cfg_file_name)
        logger.info(f"Read configuration file: {self.cfg_file_name}")
        logger.info(f"Configuration is: {self.cfg['default']}")

        self.cell_file = f"{self.cfg['default']['cell_file']}"

        # set the random seed before we use it anywhere
        random.seed(self.cfg["default"]["seed"])

        if folder is None:
            self.analyses_dir = create_analysis_dir(self.cell_file, False)
            logger.info(f"Created new directory for analyses: {self.analyses_dir}")
            # write to a file
            with open("simulation.txt", "w") as f:
                print(f"{self.analyses_dir}", file=f)

            logger.info("Copying cell folder to analyses directory")
            shutil.copytree(
                f"{self.cfg['default']['cell_dir']}", f"{self.analyses_dir}"
            )
        else:
            self.analyses_dir = folder

            # load sim data
            with open(f"{folder}/{self.recorded_segments_file}", "r") as f:
                self.recorded_segments = json.load(f)

            if self.cfg["default"]["fi_curves"] is True:
                with open(f"{folder}/{self.fi_sims_file}", "r") as f:
                    recorder_fi = json.load(f)
                    self.recorder["fi"] = recorder_fi
            if self.cfg["default"]["poisson_inputs"] is True:
                with open(f"{folder}/{self.poisson_input_sims_file}", "r") as f:
                    recorder_poisson = json.load(f)
                    self.recorder["poisson"] = recorder_poisson
                with open(f"{folder}/{self.poisson_input_segments_file}", "r") as f:
                    self.input_segment_marks = json.load(f)

        os.chdir(self.analyses_dir)

        self.nml_doc = read_neuroml2_file(
            self.cell_file
        )  # type: neuroml.NeuroMLDocument
        self.cell_obj = self.nml_doc.cells[0]  # type: neuroml.Cell
        if folder is None:
            self.__get_segments_to_record(True)
        else:
            self.__get_segments_to_record(False)

        return self.analyses_dir

    def analyse(self):
        """Main runner method for analyses"""
        self.run_model_analyses()
        self.create_sim_analyses()
        self.execute_simulations()

    def plot(self):
        """Main method for plotting."""
        self.plot_morphology()
        self.plot_sim_timeseries()

    def plot_sim_timeseries(self):
        """Plot time series data from simulations"""
        logger.info("Plotting time series")
        line_colors = []
        for segs, seginfo in self.recorded_segments.items():
            line_colors.append(seginfo["marker_color"])

        for sim_type, sims_specs in self.recorder.items():
            for k, specs in sims_specs.items():
                lems_file = specs["simfile"]
                plot_time_series_from_lems_file(
                    lems_file,
                    show_plot_already=False,
                    offset=True,
                    labels=False,
                    colors=line_colors,
                    bottom_left_spines_only=True,
                    save_figure_to=lems_file.replace(".xml", "_v.png"),
                )
                logger.info(f"Plotting time series for {lems_file}")

    def run_model_analyses(self):
        """Run analyses that can be done on the model"""
        self.plot_morphology()

    def plot_morphology(self):
        """Plot morphology with recordings marked."""
        # morphology
        if self.cfg["default"]["plot_morphology"] is True:
            logger.info("Generating morphology plots")
            plot_morphology_2d(self.cell_obj, self.recorded_segments, "morphology")

    def create_sim_analyses(self):
        """Create analyses that require simulation of the model."""
        # fi-curves with step current at soma
        if self.cfg["default"]["fi_curves"] is True:
            logger.info("Generating fi curve simulations")
            recorder_fi = {}
            if len(self.cfg["fi_curves"]["currents"]) == 0:
                currents = numpy.linspace(
                    start=convert_to_units(self.cfg["fi_curves"]["currents_min"], "nA"),
                    stop=convert_to_units(self.cfg["fi_curves"]["currents_max"], "nA"),
                    num=self.cfg["fi_curves"]["currents_steps"],
                )

                self.sim_counter = 0
                for cr in currents:
                    simid, lems_file = self.generate_step_current_sim(
                        segment_id=0, current_nA=cr
                    )
                    recorder_fi[simid] = {
                        "simfile": lems_file,
                        "segment": "0",
                        "current": cr,
                    }
                    self.sim_counter += 1

            with open(self.fi_sims_file, "w") as f:
                json.dump(recorder_fi, f)

            self.recorder["fi"] = recorder_fi

        if self.cfg["default"]["poisson_inputs"] is True:
            logger.info("Generating poisson input simulations")
            self.sim_counter = 0
            recorder_poisson = {}
            # same set of segments for each simulation, for each seed
            self.poisson_input_segments = random.sample(
                self.cell_obj.morphology.segments,
                self.cfg["poisson_inputs"]["num_inputs"],
            )

            colors = iter(
                cm.rainbow(
                    numpy.linspace(0, 1, self.cfg["poisson_inputs"]["num_inputs"])
                )
            )

            self.input_segment_marks = {}
            for sg in self.poisson_input_segments:
                self.input_segment_marks[sg.id] = {
                    "marker_size": self.cfg["default"]["segment_marker_size"],
                    "marker_color": list(next(colors)),
                }
            plot_morphology_2d(self.cell_obj, self.input_segment_marks, "inputs")

            # number of iterations with different seeds for the poisson inputs
            recorder_poisson = {}
            for i in range(0, self.cfg["poisson_inputs"]["num_iterations"]):
                simid, lems_file = self.generate_poisson_input_sim()
                recorder_poisson[simid] = {
                    "simfile": lems_file,
                }

            with open(self.poisson_input_segments_file, "w") as f:
                json.dump(self.input_segment_marks, f)

            with open(self.poisson_input_sims_file, "w") as f:
                json.dump(recorder_poisson, f)
            self.recorder["poisson"] = recorder_poisson

    def __get_segments_to_record(self, new: bool = False):
        """Get a segments to mark for recording from.

        :param new: create new segments if True, else load from a file
        :type new: bool
        """
        if not new:
            with open(self.recorded_segments_file, "r") as f:
                self.recorded_segments = json.load(f)
        else:
            self.unbranched_segment_groups = (
                self.cell_obj.get_segment_groups_by_substring("", unbranched=True)
            )
            # pick N
            sgs = list(self.unbranched_segment_groups.values())
            sgs = random.sample(sgs, self.cfg["default"]["num_segs_record"])
            nsegs = 1 + len(sgs) + len(self.cfg["default"]["extra_segments_record"])
            # unique colors
            colors = iter(cm.rainbow(numpy.linspace(0, 1, nsegs)))

            # always record from soma
            self.recorded_segments["0"] = {
                "marker_size": self.cfg["default"]["segment_marker_size"],
                "marker_color": list(next(colors)),
            }

            # from other segments around the cell
            for sg in sgs:
                segments = self.cell_obj.get_all_segments_in_group(sg)
                # middle
                self.recorded_segments[str(segments[int(len(segments) / 2)])] = {
                    "marker_size": self.cfg["default"]["segment_marker_size"],
                    "marker_color": list(next(colors)),
                }

            for s in self.cfg["default"]["extra_segments_record"]:
                self.recorded_segments[str(s)] = {
                    "marker_size": self.cfg["default"]["segment_marker_size"],
                    "marker_color": list(next(colors)),
                }

            # save recorded segments to a json file
            with open(self.recorded_segments_file, "w") as f:
                json.dump(self.recorded_segments, f)

        logger.debug(f"Segments being recorded from are: {self.recorded_segments}")

    def generate_step_current_sim(self, current_nA: str, segment_id: str):
        """Create simulation with provided current at provided point in the cell.

        Create individual simulations for each and then run them as required
        and analyse later, instead of creating a network which may not run if
        there are too many cells.

        Derived from generate_current_vs_frequency_curve in PyNeuroML.

        :param current_nA: current value in nA
        :type current_nA: str
        :param segment_id: input segment id
        :type segment_id: str
        """
        sim_id = f"step_current_sim_{self.sim_counter}"
        # sim
        ls = LEMSSimulation(
            sim_id=sim_id,
            duration=convert_to_units(self.cfg["fi_curves"]["sim_duration"], "ms"),
            dt=self.cfg["fi_curves"]["dt"],
        )
        ls.include_neuroml2_file(self.cell_file, include_included=True)
        # nml model
        net_doc = nmlu.component_factory(neuroml.NeuroMLDocument, id=sim_id)
        net_doc.add(neuroml.IncludeType(href=self.cell_file))
        net = net_doc.add(
            neuroml.Network,
            id="network",
            type="networkWithTemperature",
            temperature=self.cfg["fi_curves"]["temperature"],
            validate=False,
        )
        pop = net.add(
            neuroml.Population,
            id=f"population_of_{self.cell_obj.id}",
            component=self.cell_obj.id,
            type="populationList",
            size=1,
            validate=False,
        )
        pop.add(neuroml.Instance, id=0, location=neuroml.Location(x=0, y=0, z=0))
        ls.assign_simulation_target(net.id)

        pg = net_doc.add(
            neuroml.PulseGenerator,
            id=f"pg_{self.sim_counter}",
            delay=self.cfg["fi_curves"]["stim_start"],
            duration=self.cfg["fi_curves"]["stim_duration"],
            amplitude=f"{current_nA} nA",
        )

        # Add these to cells
        input_list = net.add(
            neuroml.InputList, id="input_0", component=pg.id, populations=pop.id
        )
        input_list.add(
            neuroml.Input,
            id="0",
            target=f"../{pop.id}/0",
            destination="synapses",
            segment_id=segment_id,
        )
        net_file_name = f"{sim_id}.net.nml"
        write_neuroml2_file(net_doc, net_file_name)
        ls.include_neuroml2_file(net_file_name)
        for f in self.cfg["default"]["extra_lems_definition_files"]:
            ls.include_lems_file(f)
        ls.create_output_file("output_file", f"{sim_id}.v.dat")

        for s in self.recorded_segments.keys():
            ls.add_column_to_output_file(
                "output_file", f"v_cell_0_{s}", f"{pop.id}/0/{self.cell_obj.id}/{s}/v"
            )

        lems_file_name = ls.save_to_file()
        return (sim_id, lems_file_name)

    def generate_poisson_input_sim(self):
        """Create simulation with a number of poisson inputs being projected on to the cell.

        Each simulation uses the same inputs, but different seeds
        """
        sim_id = f"poisson_stim_sim_{self.sim_counter}"
        # sim
        ls = LEMSSimulation(
            sim_id=sim_id,
            duration=convert_to_units(self.cfg["poisson_inputs"]["sim_duration"], "ms"),
            dt=self.cfg["poisson_inputs"]["dt"],
            simulation_seed=random.randint(0, 99999),
        )
        ls.include_neuroml2_file(self.cell_file, include_included=True)
        # nml model
        net_doc = nmlu.component_factory(neuroml.NeuroMLDocument, id=sim_id)
        net_doc.add(neuroml.IncludeType(href=self.cell_file))
        net = net_doc.add(
            neuroml.Network,
            id="network",
            type="networkWithTemperature",
            temperature=self.cfg["poisson_inputs"]["temperature"],
            validate=False,
        )
        syn = net_doc.add(
            neuroml.ExpTwoSynapse,
            id="syn",
            gbase="6nS",
            erev="0mV",
            tau_decay="10ms",
            tau_rise="2ms",
        )
        pop = net.add(
            neuroml.Population,
            id=f"population_of_{self.cell_obj.id}",
            component=self.cell_obj.id,
            type="populationList",
            size=1,
            validate=False,
        )
        pop.add(neuroml.Instance, id=0, location=neuroml.Location(x=0, y=0, z=0))
        ls.assign_simulation_target(net.id)

        ctr = 0
        # new input
        pi = net_doc.add(
            neuroml.SpikeGeneratorPoisson,
            id=f"pi_{self.sim_counter}_{ctr}",
            average_rate=f"{self.cfg['poisson_inputs']['hz_inputs']} Hz",
        )
        pi_pop = net.add(
            neuroml.Population,
            id="SpikeGeneratorPoissons",
            component=pi.id,
            size=len(self.poisson_input_segments),
        )

        pi_proj = net.add(
            neuroml.Projection,
            id="PoissonProjections",
            presynaptic_population=pi_pop.id,
            postsynaptic_population=pop.id,
            synapse=syn.id,
        )
        for s in self.poisson_input_segments:
            pi_proj.add(
                neuroml.Connection,
                id=str(ctr),
                pre_cell_id=f"../{pi_pop.id}[{ctr}]",
                pre_segment_id="0",
                pre_fraction_along="0.5",
                post_cell_id=f"../{pop.id}/0/{self.cell_obj.id}/",
                post_segment_id=str(s.id),
                post_fraction_along="0.5",
            )
            ctr += 1

        net_file_name = f"{sim_id}.net.nml"
        write_neuroml2_file(net_doc, net_file_name)
        ls.include_neuroml2_file(net_file_name)
        for f in self.cfg["default"]["extra_lems_definition_files"]:
            ls.include_lems_file(f)
        ls.create_output_file("output_file", f"{sim_id}.v.dat")

        for s in self.recorded_segments.keys():
            ls.add_column_to_output_file(
                "output_file", f"v_cell_0_{s}", f"{pop.id}/0/{self.cell_obj.id}/{s}/v"
            )

        lems_file_name = ls.save_to_file()
        return (sim_id, lems_file_name)

    def execute_simulations(self):
        """Execute simulations in parallel"""
        logger.info(f"recorder is: {self.recorder}")
        # generates all the NEURON simulations
        sims_spec = {}
        for sim_type, sims_specs in self.recorder.items():
            for k, specs in sims_specs.items():
                sims_spec[specs["simfile"]] = {
                    "engine": "jneuroml_neuron",
                    "kwargs": {
                        "nogui": True,
                        "compile_mods": False,
                        "skip_run": False,
                        "only_generate_scripts": True,
                    },
                }
        logger.info(f"sims_spec is {sims_spec}")
        run_multiple_lems_with(self.cfg["default"]["num_parallel"], sims_spec=sims_spec)

        # compile all the mods
        # we're still in the analysis dir
        execute_command_in_dir("nrnivmodl", directory=".", verbose=False)

        # run all the simulations
        cmds_spec = []
        results = None
        for sim_type, sims_specs in self.recorder.items():
            for k, specs in sims_specs.items():
                cmds_spec.append(
                    {
                        "command": f"python3 {specs['simfile'].replace('.xml', '_nrn.py')}",
                        "directory": ".",
                        "verbose": False,
                    }
                )
        logger.info(f"cmd_spec is {cmds_spec}")
        results = execute_multiple_in_dir(
            num_parallel=self.cfg["default"]["num_parallel"], cmds_spec=cmds_spec
        )
