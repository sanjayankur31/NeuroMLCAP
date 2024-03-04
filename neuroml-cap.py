#!/usr/bin/env python3
"""
Main runner script for the NeuroML Cell Analysis Pipeline (NeuroMLCAP)

File: neuroml-cap.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import os
import shutil
import tomllib
import logging
from pyneuroml.io import read_neuroml2_file
from datetime import datetime
from pyneuroml.utils import get_model_file_list
from pyneuroml.analysis import generate_current_vs_frequency_curve

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
            self.cfg = tomllib.load(f)['default']

        self.cfg_file_name = config_file_name
        logger.info(f"Read configuration file: {self.cfg_file_name}")
        logger.info(f"Configuration is: {self.cfg}")

    def __create_analysis_dir(self):
        """Create a new folder to hold the analyses results"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.analyses_dir = f"{timestamp}_{self.cfg['cell_file']}"
        os.mkdir(self.analyses_dir)

    def run(self):
        """Main runner method"""
        self.__create_analysis_dir()
        logger.info(f"Created new directory for analyses: {self.analyses_dir}")
        filelist = []
        get_model_file_list(
            self.cfg["cell_file"],
            rootdir=self.cfg["cell_dir"],
            filelist=filelist,
        )

        self.model_files = filelist
        logger.debug(f"Model files are: {self.model_files}")

        logger.info("Copying files to analyses directory")
        for f in self.model_files:
            shutil.copy(
                f"{self.cfg['cell_dir']}/{f}", f"{self.analyses_dir}/{f}"
            )

        os.chdir(self.analyses_dir)
        self.cell_file = f"{self.cfg['cell_file']}"
        self.nml_doc = read_neuroml2_file(self.cell_file)
        self.cell_obj = self.nml_doc.cells[0]

        # morphology
        if self.cfg["plot_morphology"] is True:
            logger.info("Generating morphology plots")
            from analyses.morphology.plot_morphology import plot_morpholgy_2d

            plot_morpholgy_2d(self.cell_obj)


if __name__ == "__main__":
    analysis = NeuroMLCAP()
    analysis.read_config("analysis.toml")
    analysis.run()
