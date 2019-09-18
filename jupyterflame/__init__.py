""" This magic command will run a prun magic command, 
    generate and show a famegraph from the output """

__version__ = '0.0.1'

from .jupyterflame import FlameClass
            
def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    ipython.register_magics(FlameClass)