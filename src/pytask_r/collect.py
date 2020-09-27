"""Collect tasks."""
import copy
import functools
import subprocess
from typing import Iterable
from typing import Optional
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.mark import has_marker
from _pytask.nodes import FilePathNode
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func
from _pytask.shared import to_list


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


def run_r_script(depends_on, r):
    """Run an R script."""
    script = to_list(depends_on)[0]
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
        r_function = functools.partial(r_function, r=args)

        task.function = r_function

        if isinstance(task.depends_on[0], FilePathNode) and task.depends_on[
            0
        ].value.suffix not in [".r", ".R"]:
            raise ValueError(
                "The first dependency of an R task must be the executable script."
            )

        return task


def _merge_all_markers(task):
    """Combine all information from markers for the compile r function."""
    r_marks = get_specific_markers_from_task(task, "r")
    mark = r_marks[0]
    for mark_ in r_marks[1:]:
        mark = mark.combined_with(mark_)
    return mark
