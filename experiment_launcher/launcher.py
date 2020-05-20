import os
from joblib import Parallel, delayed
import datetime
from importlib import import_module
from itertools import product


class Launcher(object):
    def __init__(self, exp_name, python_file, n_exp, memory=2000, hours=24, minutes=0, seconds=0,
                 project_name=None, base_dir=None, n_jobs=-1, use_timestamp=False):
        self._exp_name = exp_name
        self._python_file = python_file
        self._n_exp = n_exp
        self._memory = memory
        self._duration = Launcher._to_duration(hours, minutes, seconds)
        self._project_name = project_name
        self._n_jobs = n_jobs

        self._experiment_list = list()
        self._default_params = dict()

        if base_dir is None:
            self._exp_dir_local = os.path.join('.', 'logs', self._exp_name)
            self._exp_dir_slurm = os.path.join('/work', 'scratch', os.getenv('USER'), self._exp_name)
        else:
            self._exp_dir_local = os.path.join(base_dir, self._exp_name)
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
        code += '#SBATCH -J  ' + self._exp_name + '\n'
        code += '#SBATCH -a 0-' + str(self._n_exp) + '\n'
        code += '#SBATCH -t ' + self._duration + '\n'
        code += """\
#SBATCH -n 1
#SBATCH -c 1
"""
        code += '#SBATCH --mem-per-cpu=' + str(self._memory) + '\n'
        code += '#SBATCH -o ' + self._exp_dir_slurm + '/%A_%a-out.txt\n'
        code += '#SBATCH -e ' + self._exp_dir_slurm + '/%A_%a-err.txt\n'
        code += """\
###############################################################################
# Your PROGRAM call starts here
echo "Starting Job $SLURM_JOB_ID, Index $SLURM_ARRAY_TASK_ID"

# Program specific arguments
"""
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
                print('experiment' + params + default_params + ', seed=' + str(i) + ', results_dir=' + results_dir + ')')
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
    def _to_duration(hours, minutes, seconds):
        h = "0" + str(hours) if hours < 10 else str(hours)
        m = "0" + str(minutes) if minutes < 10 else str(minutes)
        s = "0" + str(seconds) if seconds < 10 else str(seconds)

        return h + ":" + m + ":" + s




