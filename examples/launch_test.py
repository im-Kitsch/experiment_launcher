from itertools import product
from experiment_launcher import Launcher

if __name__ == '__main__':
    local = True
    test = False

    launcher = Launcher(exp_name='test_launcher',
                        python_file='test',
                        n_exp=2,
                        memory=2000,
                        hours=24,
                        minutes=0,
                        seconds=0,
                        base_dir='./logs',
                        n_jobs=1,
                        use_timestamp=True)

    a_list = [1, 2, 3]
    b_c_list = [11, 12]

    launcher.add_default_params(default='b')

    for a, b_c in product(a_list, b_c_list):
        launcher.add_experiment(a=a,
                                b_c=b_c)

    launcher.run(local, test)