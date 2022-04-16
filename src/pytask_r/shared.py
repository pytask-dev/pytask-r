from __future__ import annotations

from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Sequence


_ERROR_MSG = """The old syntax for @pytask.mark.r was suddenly deprecated starting \
with pytask-r v0.2 to provide a better user experience. Thank you for your \
understanding!

It is recommended to upgrade to the new syntax, so you enjoy all the benefits of v0.2 \
of pytask and pytask-r which is among others access to 'depends_on' and 'produces', \
and other kwargs inside the R script.

You can find a manual here: \
https://github.com/pytask-dev/pytask-r/blob/v0.2.0/README.md

Upgrading can be as easy as rewriting your current task from

    @pytask.mark.r(["--option", "path_to_dependency.txt"])
    @pytask.mark.depends_on("script.R")
    @pytask.mark.produces("out.csv")
    def task_r():
        ...

to

    @pytask.mark.r(script="script.r", options="--option")
    @pytask.mark.depends_on("path_to_dependency.txt")
    @pytask.mark.produces("out.csv")
    def task_r():
        ...

You can also fix the version of pytask and pytask-r to <0.2, so you do not have to \
to upgrade. At the same time, you will not enjoy the improvements released with \
version v0.2 of pytask and pytask-r.

"""


def r(
    *args,
    script: str | Path = None,
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
    script : Union[str, Path]
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
    if args or script is None:
        raise RuntimeError(_ERROR_MSG)

    options = [] if options is None else list(map(str, _to_list(options)))
    return script, options, serializer, suffix


def _to_list(scalar_or_iter):
    """Convert scalars and iterables to list.

    Parameters
    ----------
    scalar_or_iter : str or list

    Returns
    -------
    list

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
