import os
from joblib import Parallel, delayed
import datetime
from importlib import import_module
from itertools import product


class Launcher(object):
    """
    Creates and starts jobs with Joblib or SLURM.

    """

    def __init__(self, exp_name, python_file, n_exp, n_cores=1, memory=2000, days=0, hours=24, minutes=0, seconds=0,
                 project_name=None, base_dir=None, n_jobs=-1, conda_env=None, gres=None, begin=None,
                 use_timestamp=False):
        """
        Constructor.

        Args:
            exp_name (str): name of the experiment
            python_file (str): prefix of the python file that runs a single experiment
            n_exp (int): number of experiments
            n_cores (int): number of cpu cores
            memory (int): maximum memory (slurm will kill the job if this is reached)
            days (int): number of days the experiment can last (in slurm)
            hours (int): number of hours the experiment can last (in slurm)
            minutes (int): number of minutes the experiment can last (in slurm)
            seconds (int): number of seconds the experiment can last (in slurm)
            project_name (str): name of the project for slurm. This is important if you have
                different projects (e.g. in the hhlr cluster)
            base_dir (str): path to directory to save the results (in hhlr results are saved to /work/scratch/$USER)
            n_jobs (int): number of parallel jobs in Joblib
            conda_env (str): name of the conda environment to run the experiments in
            gres (str): request cluster resources. E.g. to add a GPU in the IAS cluster specify gres='gpu:rtx2080:1'
            begin (str): start the slurm experiment at a given time (see --begin in slurm docs)
            use_timestamp (bool): add a timestamp to the experiment name

        """
        self._exp_name = exp_name
        self._python_file = python_file
        self._n_exp = n_exp
        self._n_cores = n_cores
        self._memory = memory
        self._duration = Launcher._to_duration(days, hours, minutes, seconds)
        self._project_name = project_name
        self._n_jobs = n_jobs
        self._conda_env = conda_env
        self._gres = gres
        self._begin = begin

        self._experiment_list = list()
        self._default_params = dict()

        base_dir = './logs' if base_dir is None else base_dir
        self._exp_dir_local = os.path.join(base_dir, self._exp_name)

        scratch_dir = os.path.join('/work', 'scratch', os.getenv('USER'))
        if os.path.isdir(scratch_dir):
            self._exp_dir_slurm = os.path.join(scratch_dir, self._exp_name)
        else:
            self._exp_dir_slurm = self._exp_dir_local

        if use_timestamp:
            self._exp_name += datetime.datetime.now().strftime('_%Y-%m-%d_%H-%M-%S')

    def add_experiment(self, **kwargs):
        self._experiment_list.append(kwargs)

    def add_default_params(self, **kwargs):
        self._default_params.update(kwargs)

    def run(self, local, test=False):
        if local:
            self._run_joblib(test)
        else:
            self._run_slurm(test)

        self._experiment_list = list()

    def generate_slurm(self):
        code = """\
#!/usr/bin/env bash

###############################################################################
# SLURM Configurations
"""
        if self._project_name:
            code += '#SBATCH -A ' + self._project_name + '\n'
        code += '#SBATCH -J ' + self._exp_name + '\n'
        code += '#SBATCH -a 0-' + str(self._n_exp - 1) + '\n'
        code += '#SBATCH -t ' + self._duration + '\n'
        if self._begin:
            code += '#SBATCH --begin=' + self._begin + '\n'
        code += """\
#SBATCH -n 1
"""
        code += '#SBATCH -c ' + str(self._n_cores) + '\n'
        code += '#SBATCH --mem-per-cpu=' + str(self._memory) + '\n'
        if self._gres:
            print(self._gres)
            code += '#SBATCH --gres=' + str(self._gres) + '\n'
        code += '#SBATCH -o ' + self._exp_dir_slurm + '/%A_%a-out.txt\n'
        code += '#SBATCH -e ' + self._exp_dir_slurm + '/%A_%a-err.txt\n'
        code += """\
###############################################################################
# Your PROGRAM call starts here
echo "Starting Job $SLURM_JOB_ID, Index $SLURM_ARRAY_TASK_ID"

# Program specific arguments
"""
        if self._conda_env:
            if os.path.exists('/home/{}/miniconda3'.format(os.getenv('USER'))):
                code += 'eval \"$(/home/{}/miniconda3/bin/conda shell.bash hook)\"\n'.format(os.getenv('USER'))
            elif os.path.exists('/home/{}/anaconda3'.format(os.getenv('USER'))):
                code += 'eval \"$(/home/{}/anaconda/bin/conda shell.bash hook)\"\n'.format(os.getenv('USER'))
            else:
                raise Exception('You do not have a /home/USER/miniconda3 or /home/USER/anaconda3 directories')
            code += 'conda activate {}\n\n'.format(self._conda_env)
            code += 'python ' + self._python_file + '.py \\\n'
        else:
            code += 'python3 ' + self._python_file + '.py \\\n'
        code += """\
\t\t${@:2} \\
\t\t--seed $SLURM_ARRAY_TASK_ID \\
\t\t--results-dir $1
"""
        return code

    def save_slurm(self):
        code = self.generate_slurm()

        os.makedirs(self._exp_dir_slurm, exist_ok=True)
        script_name = "slurm_" + self._exp_name + ".sh"
        full_path = os.path.join(self._exp_dir_slurm, script_name)

        with open(full_path, "w") as file:
            file.write(code)

        return full_path

    def _run_slurm(self, test):
        full_path = self.save_slurm()

        for exp in self._experiment_list:
            command_line_arguments = self._convert_to_command_line(exp)
            if self._default_params:
                command_line_arguments += ' '
                command_line_arguments += self._convert_to_command_line(self._default_params)
            results_dir = self._generate_results_dir(self._exp_dir_slurm, exp)
            command = "sbatch " + full_path + ' ' + results_dir + ' ' + command_line_arguments

            if test:
                print(command)
            else:
                os.system(command)

    def _run_joblib(self, test):
        if not test:
            os.makedirs(self._exp_dir_local, exist_ok=True)

        module = import_module(self._python_file)
        experiment = module.experiment

        if test:
            if self._default_params:
                default_params = str(self._default_params).replace('{', ', ').replace('}', ', ') \
                    .replace(': ', '=').replace('\'', '')
            else:
                default_params = ''

            for exp, i in product(self._experiment_list, range(self._n_exp)):
                results_dir = self._generate_results_dir(self._exp_dir_local, exp)
                params = str(exp).replace('{', '(').replace('}', '').replace(': ', '=').replace('\'', '')
                print('experiment' + params + default_params + 'seed=' + str(i) + ', results_dir=' + results_dir + ')')
        else:
            if hasattr(module, 'default_params'):
                params_dict = module.default_params()
            else:
                params_dict = dict()

            Parallel(n_jobs=self._n_jobs)(delayed(experiment)(**params)
                                          for params in self._generate_exp_params(params_dict))

    @staticmethod
    def _generate_results_dir(results_dir, exp):
        for key, value in exp.items():
            subfolder = key + '_' + str(value)
            results_dir = os.path.join(results_dir, subfolder)

        return results_dir

    def _generate_exp_params(self, params_dict):
        params_dict.update(self._default_params)

        for exp, i in product(self._experiment_list, range(self._n_exp)):
            params_dict.update(exp)
            params_dict['seed'] = i
            params_dict['results_dir'] = self._generate_results_dir(self._exp_dir_local, exp)

            yield params_dict

    @staticmethod
    def _convert_to_command_line(exp):
        command_line = ''
        for key, value in exp.items():
            new_command = '--' + key.replace('_', '-') + ' '

            if isinstance(value, bool):
                new_command = new_command if value else ''
            else:
                new_command += str(value) + ' '

            command_line += new_command

        return command_line

    @staticmethod
    def _to_duration(days, hours, minutes, seconds):
        h = "0" + str(hours) if hours < 10 else str(hours)
        m = "0" + str(minutes) if minutes < 10 else str(minutes)
        s = "0" + str(seconds) if seconds < 10 else str(seconds)

        return str(days) + '-' + h + ":" + m + ":" + s




