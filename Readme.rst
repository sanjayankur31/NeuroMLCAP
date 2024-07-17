NeuroMLCAP
------------

The NeuroML Cell Analysis Pipeline (NeuroMLCAP) is a utility for the easy analysis of NeuroML cell models.
It is written in Python and takes advantage of the NeuroML standard.
If your cell model is standardised in NeuroML, you can use this utility to analyse it.

More information on NeuroML can be found in its documentation at https://docs.neuroml.org.

Installation
============

Clone this repository and enter it:

.. code:: bash

    git clone https://github.com/sanjayankur31/NeuroMLCAP.git
    cd NeuroMLCAP


In most cases, you should be able to use `pip` to install the necessary requirements.
Please do remember to use a virtual environment.

.. code:: bash

    pip install -r ./requirements.txt


Usage
=====


Get the cell model to analyse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please create a new folder for the NeuroML cell model that you are looking to analyse, and copy all the necessary files to it.
This includes the cell definition file and the included channel files and so on.
(You can use `pynml-archive` to create an archive of the cell model and required files and unzip it to a new folder).

Configure your analyses
~~~~~~~~~~~~~~~~~~~~~~~

To ensure that analyses can be repeated, we provide the required information as a configuration file.
Copy the `analysis.toml` file to `analysis.<cellname>.toml` and modify it as required:

.. code:: bash

    cp analysis.toml analysis.<cellname>.toml

As more analyses are added to the suite, the configuration file will continue to grow.

Run the analyses
~~~~~~~~~~~~~~~~~

To run the complete analysis pipeline, run:

.. code:: bash

    python neuroml-cap.py --analyse analysis.<cellname>.toml


This will create a new folder with the simulation data.


Plotting simulation outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similarly, to plot the generated reports/graphs, run:

.. code:: bash

    python neuroml-cap.py --plot <output folder> analysis.<cellname>.toml


This allows re-generation of the graphs/plots without having to re-run the analyses.

NeuroMLCAP uses Matplotlib for all its plotting.
You can customise Matplotlib settings using a `matplotlibrc` configuration file.
One is included as an example.
Please see the `Matplotlib documentation <https://matplotlib.org/stable/users/explain/customizing.html>`__ for more information.

List of analyses
================

The analysis pipeline is currently being developed.

The list of analyses will grow as more of them are added.
To request inclusion of a particular analysis protocol, please file a new issue.

F-I curve
~~~~~~~~~

Generate an F-I curve for the cell by simulating it with a range of step currents

Configuration:

- currents_min: minimum current input for step current
- currents_max: maximum current input for step current
- currents_steps: number of steps between minimum and maximum current
- currents: list of explicit current values to provide
- dt: simulation time step
- temperature: temperature for simulation (for temperature sensitive ion channels, eg: "32degC")
- stim_start: start time of current step stimulation
- stim_duration: duration of current step simulation
- sim_duration: total simulation duration


Output characteristics with random (Poisson) inputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate plots of the behaviour of the cell when given Poisson inputs at different parts of its cell morphology.

Configuration:

- num_inputs: number of Poisson inputs
- hz_inputs: frequency of inputs
- num_iterations: number of iterations
- dt: simulation time step
- temperature: temperature for simulation (for temperature sensitive ion channels, eg: "32degC")
- sim_duration: total simulation duration
