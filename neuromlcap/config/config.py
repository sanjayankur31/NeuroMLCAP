#!/usr/bin/env python3
"""
Configuration related code

File: neuromlcap/config/config.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import logging
import tomllib


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_config(config_file_name: str = "analysis.toml"):
    """Read the analysis configuration file

    :param config_file_name: name of configuration file
    """
    with open(config_file_name, "rb") as f:
        return tomllib.load(f)
