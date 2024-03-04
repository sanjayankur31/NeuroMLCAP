#!/usr/bin/env python3
"""
Main runner script for the NeuroML Cell Analysis Pipeline (NeuroMLCAP)

File: neuroml-cap.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import os
import numpy
import itertools
import shutil
import tomllib
import logging
from pyneuroml.io import read_neuroml2_file, write_neuroml2_file
from datetime import datetime
from pyneuroml.utils import get_model_file_list
from pyneuroml.utils.units import convert_to_units
from pyneuroml.lems.LEMSSimulation import LEMSSimulation
import neuroml
import neuroml.utils as nmlu


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NeuroMLCAP(object):
    """Main class for NeuroMLCAP"""

    def __init__(self):
        """Initialise"""
        self.cfg_file_name = None
        self.cfg = None
        self.nml_doc = None
        self.cell = None
        self.analyses_dir = None
        self.model_files = None

    def read_config(self, config_file_name: str):
        """Read the analysis configuration file

        :param config_file_name: TODO
        """
        with open(config_file_name, 'rb') as f:
            self.cfg = tomllib.load(f)

        self.cfg_file_name = config_file_name
        logger.info(f"Read configuration file: {self.cfg_file_name}")
        logger.info(f"Configuration is: {self.cfg['default']}")

    def __create_analysis_dir(self):
        """Create a new folder to hold the analyses results"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.analyses_dir = f"{timestamp}_{self.cfg['default']['cell_file']}"
        os.mkdir(self.analyses_dir)

    def run(self):
        """Main runner method"""
        self.__create_analysis_dir()
        logger.info(f"Created new directory for analyses: {self.analyses_dir}")
        filelist = []
        get_model_file_list(
            self.cfg['default']["cell_file"],
            rootdir=self.cfg['default']["cell_dir"],
            filelist=filelist,
        )

        # nml files and LEMS definition files
        self.model_files = filelist + self.cfg['default']['extra_lems_definition_files']
        logger.debug(f"Model files are: {self.model_files}")

        logger.info("Copying files to analyses directory")
        for f in self.model_files:
            shutil.copy(
                f"{self.cfg['default']['cell_dir']}/{f}", f"{self.analyses_dir}/{f}"
            )

        os.chdir(self.analyses_dir)
        self.cell_file = f"{self.cfg['default']['cell_file']}"
        self.nml_doc = read_neuroml2_file(self.cell_file)
        self.cell_obj = self.nml_doc.cells[0]

        # morphology
        if self.cfg['default']["plot_morphology"] is True:
            logger.info("Generating morphology plots")
            from analyses.morphology.plot_morphology import plot_morpholgy_2d

            plot_morpholgy_2d(self.cell_obj)

        # fi-curves
        self.sim_counter = 0
        if self.cfg['default']["fi_curves"] is True:
            logger.info("Generating fi_curves")
            if len(self.cfg['fi_curves']['currents']) == 0:
                currents = numpy.linspace(
                    start=convert_to_units(self.cfg['fi_curves']['currents_min'], "nA"),
                    stop=convert_to_units(self.cfg['fi_curves']['currents_max'], "nA"),
                    num=self.cfg['fi_curves']['currents_steps'])

                input_segments = [0]
                input_segments.extend(self.cfg['fi_curves']['extra_segments'])

                args = itertools.product(input_segments, currents)

                sims = {}
                for sg, cr in args:
                    simid, lems_file = self.generate_step_current_sim(segment_id=sg, current_nA=cr)
                    sims[simid] = {
                        "simfile": lems_file,
                        "segment": sg,
                        "current": cr
                    }

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
        sim_id = f"sim_{self.sim_counter}"
        # sim
        ls = LEMSSimulation(sim_id=sim_id,
                            duration=convert_to_units(self.cfg['fi_curves']['sim_duration'], "ms"),
                            dt=self.cfg['fi_curves']['dt'])
        ls.include_neuroml2_file(self.cell_file, include_included=True)
        # nml model
        net_doc = nmlu.component_factory(neuroml.NeuroMLDocument, id=sim_id)
        net_doc.add(neuroml.IncludeType(href=self.cell_file))
        net = net_doc.add(neuroml.Network, id="network", type="networkWithTemperature",
                          temperature=self.cfg['fi_curves']['temperature'],
                          validate=False)
        pop = net.add(neuroml.Population, id="population_of_%s" % self.cell_obj.id,
                      component=self.cell_obj.id, size=1, validate=False)
        ls.assign_simulation_target(net.id)

        pg = net_doc.add(neuroml.PulseGenerator,
                         id=f"pg_{self.sim_counter}",
                         delay=self.cfg['fi_curves']['stim_start'],
                         duration=self.cfg['fi_curves']['stim_duration'],
                         amplitude=f"{current_nA} nA",
                         )

        # Add these to cells
        input_list = net.add(neuroml.InputList, id="input_0", component=pg.id, populations=pop.id)
        input_list.add(neuroml.Input,
                       id="0",
                       target=f"../{pop.id}[0]",
                       destination="synapses",
                       segment_id=segment_id,
                       )
        net_file_name = f"{sim_id}.net.nml"
        write_neuroml2_file(net_doc, net_file_name)
        ls.include_neuroml2_file(net_file_name)
        for f in self.cfg['default']['extra_lems_definition_files']:
            ls.include_lems_file(f)
        ls.create_output_file("output_file", f"{sim_id}.v.dat")

        quantity = f"{pop.id}[0]/v"
        ls.add_column_to_output_file("output_file", "v_cell_0", quantity)

        lems_file_name = ls.save_to_file()
        self.sim_counter += 1
        return (sim_id, lems_file_name)


if __name__ == "__main__":
    analysis = NeuroMLCAP()
    analysis.read_config("analysis.toml")
    analysis.run()
