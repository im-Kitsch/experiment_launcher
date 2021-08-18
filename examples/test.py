import os

from experiment_launcher import run_experiment, save_args, parse_args


def experiment(a: int = 1,
               b_c: int = 1,
               boolean: bool = True,
               default: str = 'dft',
               seed: int = 0,  # This argument is mandatory
               results_dir: str = '/tmp'  # This argument is mandatory
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


if __name__ == '__main__':
    # Leave unchanged
    args = parse_args(experiment)
    run_experiment(experiment, args)
