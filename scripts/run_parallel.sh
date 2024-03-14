#!/bin/bash

# Copyright 2024 Ankur Sinha
# Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
# File : run_parallel.sh: run pylems using gnu parallel

numfiles="$(ls LEMS*xml | wc -l)"
numprocesses=""

if [ $# -ne 1 ]
then
    echo ">> Only takes one argument: number of parallel processes or \"all\". Exiting"
    exit 1
else
    if [ "all" == $1 ]
    then
        echo ">> Running with all possible processors"
        numprocesses="-j"
    else
        echo ">> Running with ${1} processors"
        numprocesses="-j${1}"
    fi
fi

echo ">> Generating NEURON scripts for ${numfiles} simulations"
for f in LEMS*xml
do
    pynml "$f" -neuron -nogui
done

echo ">> Compiling all mod files"
nrnivmodl .

echo ">> Running $numfiles total simulations, ${1} in parallel"
ls LEMS*_nrn.py | parallel --progress $numprocesses --total $numfiles "python3 {}"
