"""Register hook specifications and implementations."""
from __future__ import annotations

from pluggy import PluginManager
from pytask import hookimpl
from pytask_r import collect
from pytask_r import config
from pytask_r import execute


@hookimpl
def pytask_add_hooks(pm: PluginManager) -> None:
    """Register hook implementations."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
