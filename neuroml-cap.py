#!/usr/bin/env python3
"""
Main entry point script

File: neuroml-cap.py

Copyright 2024 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""

import argparse

from neuromlcap.analysis.analysis import NeuroMLCAP


def neuromlcap():
    """Main runner method"""
    parser = argparse.ArgumentParser(
        prog="neuroml-cap",
        description="An automated NeuroML cell analysis pipeline",
    )

    parser.add_argument("config_file")
    tasks = parser.add_mutually_exclusive_group(required=True)
    tasks.add_argument(
        "--full", action="store_true", help="Create and execute analyses, and plot"
    )
    tasks.add_argument(
        "--analyse", action="store_true", help="Create and execute analyses"
    )
    tasks.add_argument(
        "--plot", action="store", help="Plot analysis results", metavar="folder"
    )

    args = parser.parse_args()
    analysis = NeuroMLCAP(args.config_file)
    # if both are given, do it all
    if args.full:
        analysis.prepare(folder=None)
        analysis.analyse()
        analysis.plot()
    elif args.analyse:
        analysis.prepare(folder=None)
        analysis.analyse()
    elif args.plot:
        analysis.prepare(args.plot)
        analysis.plot()
    else:
        print("Not sure what to do. Exiting.")


if __name__ == "__main__":
    neuromlcap()
