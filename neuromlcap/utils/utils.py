#!/usr/bin/env python3
"""
Misc utilities

File: neuromlcap/utils/utils.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_analysis_dir(cell_name: str, mkdir: bool = False) -> str:
    """Create a new folder to hold the analyses results

    :param cell_name: name of cell
    :type cell_name: str

    :returns: name of analyses directory
    :rtype: str
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    analyses_dir = f"{timestamp}_{cell_name}"
    if mkdir:
        os.mkdir(analyses_dir)

    return analyses_dir
