try:
    from .launcher import Launcher, get_default_params, run_experiment, add_launcher_base_args, save_args, save_success
except ImportError:
    pass

__version__ = '1.2'
