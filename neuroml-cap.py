#!/usr/bin/env python3
"""
Main runner script for the NeuroML Cell Analysis Pipeline (NeuroMLCAP)

File: neuroml-cap.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import configparser
import logging
from pyneuroml.io import read_neuroml2_file

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NeuroMLCAP(object):

    """Main class for NeuroMLCAP"""

    def __init__(self):
        """Initialise """
        self.cfg_file_name = None
        self.cfg = None
        self.nml_doc = None
        self.cell = None

    def read_config(self, config_file_name: str):
        """Read the analysis configuration file

        :param config_file_name: TODO
        """
        self.cfg = configparser.RawConfigParser()
        self.cfg.read(config_file_name)
        self.cfg_file_name = config_file_name
        logger.info(f"Read configuration file: {self.cfg_file_name}")
        logger.info(f"Configuration is: {self.cfg}")

    def run(self):
        """Main runner method
        """
        self.nml_doc = read_neuroml2_file(self.cfg.cell_file)
        self.cell = self.nml_doc.cells[0]

        # morphology
        if self.cfg.getboolean('NeuroMLCAP', 'plot_morphology') is True:
            logger.debug("Generating morphology plots")
            from analyses.morphology.plot_morphology import plot_morpholgy_2d
            plot_morpholgy_2d(self.nml_doc)


if __name__ == "__main__":
    analysis = NeuroMLCAP()
    analysis.read_config("analysis.cfg")
    analysis.run()
