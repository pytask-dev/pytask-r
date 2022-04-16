"""Parametrize tasks."""
from __future__ import annotations

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Attach parametrized r arguments to the function with a marker."""
    if callable(obj):
        if "r" in kwargs:
            pytask.mark.r(**kwargs.pop("r"))(obj)
