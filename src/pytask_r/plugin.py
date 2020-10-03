"""Register hook specifications and implementations."""
from _pytask.config import hookimpl
from pytask_r import collect
from pytask_r import config
from pytask_r import execute
from pytask_r import parametrize


@hookimpl
def pytask_add_hooks(pm):
    """Register hook implementations."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
    pm.register(parametrize)
