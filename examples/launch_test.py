import os
from itertools import product
from experiment_launcher import Launcher


if __name__ == '__main__':
    LOCAL = False
    TEST = False
    USE_CUDA = False

    # JOBLIB_PARALLEL_JOBS = os.cpu_count()
    JOBLIB_PARALLEL_JOBS = 5
    N_SEEDS = 13

    launcher = Launcher(exp_name='test_launcher',
                        python_file='test',
                        # project_name='project01234',
                        n_exp=N_SEEDS,
                        joblib_n_jobs=JOBLIB_PARALLEL_JOBS,
                        n_cores=JOBLIB_PARALLEL_JOBS * 1,
                        memory=JOBLIB_PARALLEL_JOBS * 1000,
                        days=0,
                        hours=0,
                        minutes=2,
                        seconds=0,
                        partition='test30m',
                        conda_env='base',
                        gres='gpu:rtx2080:1' if USE_CUDA else None,
                        use_timestamp=True,
                        use_underscore_argparse=False,
                        randomize_seeds=False
                        )

    a_list = [1, 2, 3]
    b_c_list = [11, 12]
    boolean_list = [True, False]

    launcher.add_default_params(default='b')

    for a, b_c, boolean in product(a_list, b_c_list, boolean_list):
        launcher.add_experiment(a=a,
                                b_c=b_c,
                                boolean=boolean)

    launcher.run(LOCAL, TEST)
