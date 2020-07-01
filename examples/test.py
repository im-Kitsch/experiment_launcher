import os
import argparse


def experiment(a, b_c, boolean, seed, results_dir,  default):

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


def default_params():
    defaults = dict(
        a=1,
        b_c=2,
        boolean=False,
        default='a'
    )

    return defaults


def parse_args():
    parser = argparse.ArgumentParser()

    arg_test = parser.add_argument_group('Test')
    arg_test.add_argument("--a", type=int)
    arg_test.add_argument("--b-c", type=int)
    arg_test.add_argument("--boolean", action='store_true')
    arg_test.add_argument('--default', type=str)

    arg_default = parser.add_argument_group('Default')
    arg_default.add_argument('--seed', type=int)
    arg_default.add_argument('--results-dir', type=str)

    parser.set_defaults(**default_params())
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    args = parse_args()
    experiment(**args)
