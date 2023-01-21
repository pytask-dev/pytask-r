"""Parametrize tasks."""
from __future__ import annotations

from typing import Any

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj: Any, kwargs: dict[Any, Any]) -> None:
    """Attach parametrized r arguments to the function with a marker."""
    if callable(obj) and "r" in kwargs:  # noqa: PLR2004
        pytask.mark.r(**kwargs.pop("r"))(obj)
