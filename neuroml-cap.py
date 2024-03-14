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
    """TODO: Docstring for neuromlcap."""
    parser = argparse.ArgumentParser(
        prog="neuroml-cap",
        description="A semi automated NeuroML cell analysis pipeline",
    )

    parser.add_argument("config_file")
    tasks = parser.add_mutually_exclusive_group(required=True)
    tasks.add_argument("--analyse", action="store_true", help="Create analyses")
    tasks.add_argument(
        "--plot", action="store", help="Plot analysis results", metavar="folder"
    )

    args = parser.parse_args()
    analysis = NeuroMLCAP(args.config_file)
    if args.analyse:
        analysis.prepare()
        analysis.analyse()
    elif args.plot:
        analysis.prepare(args.plot)
        print(f"Will plot {args.plot}")


if __name__ == "__main__":
    neuromlcap()
