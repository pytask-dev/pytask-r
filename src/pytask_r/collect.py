"""Collect tasks."""
import copy
import functools
import subprocess
from pathlib import Path
from typing import Iterable
from typing import Optional
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.mark import has_marker
from _pytask.nodes import FilePathNode
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func


def r(options: Optional[Union[str, Iterable[str]]] = None):
    """Specify command line options for Rscript.

    Parameters
    ----------
    options : Optional[Union[str, Iterable[str]]]
        One or multiple command line options passed to Rscript.

    """
    if options is None:
        options = ["--vanilla"]
    elif isinstance(options, str):
        options = [options]
    return options


def run_r_script(depends_on, r, r_source_key):
    """Run an R script."""
    script = _get_node_from_dictionary(depends_on, r_source_key)
    subprocess.run(["Rscript", script.as_posix(), *r], check=True)


@hookimpl
def pytask_collect_task(session, path, name, obj):
    """Collect a task which is a function.

    There is some discussion on how to detect functions in this `thread
    <https://stackoverflow.com/q/624926/7523785>`_. :class:`types.FunctionType` does not
    detect built-ins which is not possible anyway.

    """
    if name.startswith("task_") and callable(obj) and has_marker(obj, "r"):
        task = PythonFunctionTask.from_path_name_function_session(
            path, name, obj, session
        )
        r_function = _copy_func(run_r_script)
        r_function.pytaskmark = copy.deepcopy(task.function.pytaskmark)

        merged_marks = _merge_all_markers(task)
        args = r(*merged_marks.args, **merged_marks.kwargs)
        r_function = functools.partial(
            r_function, r=args, r_source_key=session.config["r_source_key"]
        )

        task.function = r_function

        return task


@hookimpl
def pytask_collect_task_teardown(task):
    """Perform some checks."""
    if get_specific_markers_from_task(task, "r"):
        source = _get_node_from_dictionary(task.depends_on, "source")
        if isinstance(source, FilePathNode) and source.value.suffix not in [".r", ".R"]:
            raise ValueError(
                "The first dependency of an R task must be the executable script."
            )


def _get_node_from_dictionary(obj, key, fallback=0):
    if isinstance(obj, Path):
        pass
    elif isinstance(obj, dict):
        obj = obj.get(key) or obj.get(fallback)
    return obj


def _merge_all_markers(task):
    """Combine all information from markers for the compile r function."""
    r_marks = get_specific_markers_from_task(task, "r")
    mark = r_marks[0]
    for mark_ in r_marks[1:]:
        mark = mark.combined_with(mark_)
    return mark
