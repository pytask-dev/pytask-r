import copy
import functools
import subprocess
from typing import Iterable
from typing import Optional
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.mark import has_marker
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
    script = to_list(depends_on)[0]
    subprocess.run(["Rscript", script.as_posix(), *r])


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

        args = _create_command_line_arguments(task)
        r_function = functools.partial(r_function, r=args)

        task.function = r_function

        if task.depends_on[0].value.suffix not in [".r", ".R"]:
            raise ValueError(
                "The first dependency of an R task must be the script which will be "
                "executed."
            )

        return task


def _create_command_line_arguments(task):
    r_marks = get_specific_markers_from_task(task, "r")
    mark = r_marks[0]
    for mark_ in r_marks[1:]:
        mark = mark.combine_with(mark_)

    options = r(*mark.args, **mark.kwargs)

    return options
