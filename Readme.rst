NeuroMLCAP
------------

The NeuroML Cell Analysis Pipeline is a set of Python scripts for the easy analysis of NeuroML cell models.

Installation
============

In most cases, you should be able to use `pip` to install the necessary requirements.
Please do remember to use a virtual environment.

.. code:: bash

    pip install -r ./requirements.txt


Note that if you are using GCC version 14, you will need to export some compilation flags to get `datrie (a dependency of snakemake) to install <https://github.com/pytries/datrie/issues/101>`__:

.. code:: bash

    export CFLAGS="-Wno-error=incompatible-pointer-types" ; export CXXFLAGS="-Wno-error=incompatible-pointer-types"
    pip install -r ./requirements.txt


Usage
=====


Get the cell model to analyse
=============================

Please create a new folder for the NeuroML cell model that you are looking to analyse, and copy all the necessary files to it.
This includes the cell definition file and the included channel files and so on.
(You can use `pynml-archive` to create an archive of the cell model and required files and unzip it to a new folder).

Configure your analyses
=======================

To ensure that analyses can be repeated, we provide the required information as a configuration file.
Copy the `analysis.toml` file to `analysis.<cellname>.toml` and modify it as required:

.. code:: bash

    cp analysis.toml analysis.<cellname>.toml

As more analyses are added to the suite, the configuration file will continue to grow.

Run the analyses
=================

To run the complete analysis pipeline, we currently use `snakemake <https://snakemake.github.io/>`__.
We provide the analyses cell name as a configuration option and run `snakemake`:

.. code:: bash

    snakemake --config cellname="<cellname>"


This will run all the steps of the analyses and store the results in a new folder.
