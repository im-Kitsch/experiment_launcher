# Experiment Launcher

Launch experiments locally or on a cluster running SLURM in a single file.  

## Description 

The ``experiment_launcher`` package provides a way to run multiple experiments using
SLURM or Joblib, 
with minimum effort - you just have to set the "local" parameter to True for Joblib,
and to False for SLURM. 

## Installation

You can do a minimal installation of ``experiment_launcher`` with:
```
pip3 install  -e .
```

## How to Use

- Create in your own project two files [test.py](examples/test.py)
  and [launch_test.py](examples/launch_test.py)

- Create an experiment file as in [test.py](examples/test.py)
  - This file consists of the function: `experiment`; and the
    `if __name__ == '__main__'` block
  - The function `experiment` is the core of your experiment
    - It takes as arguments your experiment settings (e.g., the number of layers in a neural 
      network, the learning rate, ...)
    - The arguments need to be assigned a default value in the function definition
    - The arguments `seed` and `results_dir` **must** always be included
    - By default, `results_dir` is the `/path_to_your_sub_experiment`
  - In `if __name__ == '__main__'` simply include:
    ```
    if __name__ == '__main__':
        run_experiment(experiment)
    ```

- Create a launcher file as in [launch_test.py](examples/launch_test.py)
  - Specify the running configurations by calling a `Launcher` constructor:
    - `n_exps` is the number of random seeds for each single experiment configuration 
    - If `joblib_n_jobs > 0`, then each node will run `joblib_n_jobs` experiments possibly in parallel.
      E.g., if `joblib_n_jobs` is `3`, then `3` jobs will run in parallel, even if `n_cores` is `1`.
      For better performance, one should specify `n_cores >= joblib_n_jobs * 1`
  - Create a single experiment configuration
    - Use `launcher.add_default_params` to add parameters shared across configurations (e.g., the dataset)
    - Use `launcher.add_experiment` to create a particular configuration (e.g., different learning rates)

- To run the experiment call
  ```
  cd examples
  python launch_test.py
  ```
- Log files will be placed in 
  - `./logs` if running locally
  - `/work/scratch/USERNAME` (the default for the `Lichtenberg-Hochleistungsrechner of the TU Darmstadt`) 

## Notes
- The seeds are created sequentially from `0` to `n_exps-1`

