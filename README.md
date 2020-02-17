# experiment_launcher

Repository for the experiment launcher class.

## What is experiment_launcher 
``experiment_launcher`` provides the launcher class.
Using this class is possible to run multiple experiments using SLURM or Joblib, 
with minimum effort: you just have to set the "local" parameter to True for joblib,
and to False for SLURM run. 

## Installation

You can do a minimal installation of ``experiment_launcher`` with:

    pip3 install  -e .