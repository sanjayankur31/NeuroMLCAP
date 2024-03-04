#!/bin/bash

# Copyright 2024 Ankur Sinha
# Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com> 
# File : run_parallel.sh: run pylems using gnu parallel

numfiles="$(ls LEMS*xml | wc -l)"
numfiles=$((numfiles - 1))
numprocesses="$1"

echo "Running $numfiles total simulations, $numprocesses in parallel"

for f in LEMS*xml
do
    pynml "$f" -neuron -nogui
done

nrnivmodl .

echo "Running $numfiles total simulations, $numprocesses in parallel"
ls LEMS*_nrn.py | parallel --progress -j$numprocesses --total $numfiles "python3 {}"
