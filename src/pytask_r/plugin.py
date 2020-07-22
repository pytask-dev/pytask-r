import pytask
from pytask_r import collect
from pytask_r import execute
from pytask_r import parametrize


@pytask.hookimpl
def pytask_add_hooks(pm):
    pm.register(collect)
    pm.register(execute)
    pm.register(parametrize)
