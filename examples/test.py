import argparse
import os
import time

from experiment_launcher import get_default_params, run_experiment, add_launcher_base_args
from experiment_launcher.launcher import save_args


def experiment(a=1,
               b_c=1,
               boolean=True,
               default='dft',
               seed=0,  # This argument is mandatory
               results_dir='/tmp'  # This argument is mandatory
               ):

    ####################################################################################################################
    # SETUP
    # Create results directory
    results_dir = os.path.join(results_dir, str(seed))
    os.makedirs(results_dir, exist_ok=True)
    # Save arguments
    save_args(results_dir, locals(), git_repo_path='./')

    ####################################################################################################################
    # EXPERIMENT
    filename = os.path.join(results_dir, 'log_' + str(seed) + '.txt')
    os.makedirs(results_dir, exist_ok=True)
    print('Running experiment with seed', str(seed),
          'and parameters a =', str(a),
          'b_c =', str(b_c),
          'boolean =', str(boolean),
          'default =', default)
    with open(filename, 'w') as file:
        file.write('Default parameters:\n')
        file.write('seed: ' + str(seed) + '\n')
        file.write('results_dir: ' + str(results_dir) + '\n')

        file.write('Experiment parameters:\n')
        file.write('a: ' + str(a) + '\n')
        file.write('b-c: ' + str(b_c) + '\n')
        file.write('boolean: ' + str(boolean) + '\n')
        file.write('default: ' + default + '\n')


def parse_args():
    parser = argparse.ArgumentParser()

    # Place your experiment arguments here
    arg_test = parser.add_argument_group('Test')
    arg_test.add_argument("--a", type=int)
    arg_test.add_argument("--b-c", type=int)
    arg_test.add_argument("--boolean", action='store_true')
    arg_test.add_argument('--default', type=str)

    # Leave unchanged
    parser = add_launcher_base_args(parser)
    parser.set_defaults(**get_default_params(experiment))
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    # Leave unchanged
    args = parse_args()
    run_experiment(experiment, args)
