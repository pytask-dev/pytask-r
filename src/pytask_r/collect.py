"""Collect tasks."""
from __future__ import annotations

import functools
import subprocess
from types import FunctionType
from typing import Iterable
from typing import Sequence

from pytask import depends_on
from pytask import FilePathNode
from pytask import has_mark
from pytask import hookimpl
from pytask import parse_nodes
from pytask import produces
from pytask import remove_marks
from pytask import Task


def r(options: str | Iterable[str] | None = None):
    """Specify command line options for Rscript.

    Parameters
    ----------
    options : Optional[Union[str, Iterable[str]]]
        One or multiple command line options passed to Rscript.

    """
    options = [] if options is None else _to_list(options)
    options = [str(i) for i in options]
    return options


def run_r_script(options):
    """Run an R script."""
    print("Executing " + " ".join(options) + ".")  # noqa: T001
    subprocess.run(options, check=True)


@hookimpl
def pytask_collect_task(session, path, name, obj):
    """Perform some checks."""
    __tracebackhide__ = True

    if has_mark(obj, "r"):
        obj, marks = remove_marks(obj, "r")

        r_mark = _merge_all_markers(marks)
        obj.pytask_meta.markers.append(r_mark)

        dependencies = parse_nodes(session, path, name, obj, depends_on)
        products = parse_nodes(session, path, name, obj, produces)

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []
        kwargs = obj.pytask_meta.kwargs if hasattr(obj, "pytask_meta") else {}

        task = Task(
            base_name=name,
            path=path,
            function=_copy_func(run_r_script),
            depends_on=dependencies,
            produces=products,
            markers=markers,
            kwargs=kwargs,
        )

        args = r(*r_mark.args, **r_mark.kwargs)
        options = _prepare_cmd_options(session, task, args)

        task.function = functools.partial(task.function, options=options)

        source = _get_node_from_dictionary(task.depends_on, "source")
        if isinstance(source, FilePathNode) and source.value.suffix not in [".r", ".R"]:
            raise ValueError(
                "The first dependency of an R task must be the executable script."
            )

        return task


def _get_node_from_dictionary(obj, key, fallback=0):
    """Get node from dictionary."""
    if isinstance(obj, dict):
        obj = obj.get(key) or obj.get(fallback)
    return obj


def _merge_all_markers(marks):
    """Combine all information from markers for the compile r function."""
    mark = marks[0]
    for mark_ in marks[1:]:
        mark = mark.combined_with(mark_)
    return mark


def _prepare_cmd_options(session, task, args):
    """Prepare the command line arguments to execute the do-file.

    The last entry changes the name of the log file. We take the task id as a name which
    is unique and does not cause any errors when parallelizing the execution.

    """
    source = _get_node_from_dictionary(task.depends_on, session.config["r_source_key"])
    return ["Rscript", source.path.as_posix(), *args]


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


def _copy_func(func: FunctionType) -> FunctionType:
    """Create a copy of a function.

    Based on https://stackoverflow.com/a/13503277/7523785.

    Example
    -------
    >>> def _func(): pass
    >>> copied_func = _copy_func(_func)
    >>> _func is copied_func
    False

    """
    new_func = FunctionType(
        func.__code__,
        func.__globals__,
        name=func.__name__,
        argdefs=func.__defaults__,
        closure=func.__closure__,
    )
    new_func = functools.update_wrapper(new_func, func)
    new_func.__kwdefaults__ = func.__kwdefaults__
    return new_func
