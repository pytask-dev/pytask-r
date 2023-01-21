"""This module contains shared functions."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Sequence


R_SCRIPT_KEY = "__script"


def r(
    *,
    script: str | Path,
    options: str | Iterable[str] | None = None,
    serializer: str | Callable[..., str] | str | None = None,
    suffix: str | None = None,
) -> tuple[
    str | Path | None,
    str | Iterable[str] | None,
    str | Callable[..., str] | str | None,
    str | None,
]:
    """Parse input to the ``@pytask.mark.r`` decorator.

    Parameters
    ----------
    script : str | Path
        The path to the R script which is executed.
    options : str | Iterable[str]
        One or multiple command line options passed to Rscript.
    serializer: Callable[Any, str] | None
        A function to serialize data for the task which accepts a dictionary with all
        the information. If the value is `None`, use either the value specified in the
        configuration file under ``r_serializer`` or fall back to ``"json"``.
    suffix: str | None
        A suffix for the serialized file. If the value is `None`, use either the value
        specified in the configuration file under ``r_suffix`` or fall back to
        ``".json"``.

    """
    options = [] if options is None else list(map(str, _to_list(options)))
    return script, options, serializer, suffix


def _to_list(scalar_or_iter: Any) -> list[Any]:
    """Convert scalars and iterables to list.

    Examples
    --------
    >>> _to_list("a")
    ['a']
    >>> _to_list(["b"])
    ['b']

    """
    return (
        [scalar_or_iter]
        if isinstance(scalar_or_iter, str) or not isinstance(scalar_or_iter, Sequence)
        else list(scalar_or_iter)
    )
