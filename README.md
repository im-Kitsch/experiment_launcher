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

## How to Use

- Create an experiment file as in [test.py](examples/test.py)
  - This file consists of two base functions: `experiment`, `parse_args`; and `if __name__ == '__main__'`
  - The function `experiment` is the core of your experiment
    - It takes as arguments your experiment settings (e.g., the number of layers in a neural network,
      the learning rate, ...)
    - The arguments need to be assigned a default value in the function definition
    - The arguments `seed` and `results_dir` **must** always be included
    - By default, `results_dir` is of the form `/path_to_your_sub_experiment/seed`
  - The function `parse_args` includes a CLI `ArgumentParser`
    - In this function you should define the command line arguments
    - These arguments **must** be the same as the ones define in the function `experiment`
    - You don't need to define the arguments `seed` and `results_dir`, as these are defined in function
      `add_launcher_base_args`
  - In `if __name__ == '__main__'` simply include
    ```
    args = parse_args()
    run_experiment(experiment, args)
    ```

- Create a launcher file as in [launch_test.py](examples/launch_test.py) 
  - TODO
  - If `joblib_n_jobs` is `None`, ASDASDASDASDAS 
  - If `joblib_n_jobs` is `3`, then `3` jobs will run in parallel, even if the `n_cores` is `1`.
    For better performance, one should specify `n_cores >= joblib_n_jobs * 1`

- To run the experiment call
  ```
  python launch_test.py
  ```
    

## Some notes
- The seeds are created sequentially from 0 to `n_exps`

