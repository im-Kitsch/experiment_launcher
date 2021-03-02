from itertools import product
from experiment_launcher import Launcher

if __name__ == '__main__':
    local = False
    test = True
    use_cuda = True

    launcher = Launcher(exp_name='test_launcher',
                        python_file='test',
                        project_name='project01234',
                        n_exp=2,
                        memory=0,
                        days=1,
                        hours=23,
                        minutes=59,
                        seconds=0,
                        n_jobs=1,
                        conda_env='conda-env',
                        gres='gpu:rtx2080:1' if use_cuda else None,
                        use_timestamp=True)

    a_list = [1, 2, 3]
    b_c_list = [11, 12]
    boolean_list = [True, False]

    launcher.add_default_params(default='b')

    for a, b_c, boolean in product(a_list, b_c_list, boolean_list):
        launcher.add_experiment(a=a,
                                b_c=b_c,
                                boolean=boolean)

    launcher.run(local, test)
