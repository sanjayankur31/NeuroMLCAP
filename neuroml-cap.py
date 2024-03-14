#!/usr/bin/env python3
"""
Main entry point script

File: neuroml-cap.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""

import sys
from neuromlcap.analysis.analysis import NeuroMLCAP


if __name__ == "__main__":
    if len(sys.argv) > 1:
        analysis = NeuroMLCAP(sys.argv[1])
    else:
        analysis = NeuroMLCAP("analysis.toml")
    analysis.run()
