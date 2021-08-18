try:
    from .launcher import Launcher, get_default_params, run_experiment, add_launcher_base_args, save_args, \
        translate_exp_params_to_argparse, parse_args
except ImportError:
    pass

__version__ = '1.2'
