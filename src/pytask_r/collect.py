import copy
import functools
import subprocess

import pytask
from pytask.mark import get_markers_from_task
from pytask.mark import has_marker
from pytask.nodes import PythonFunctionTask
from pytask.parametrize import _copy_func
from pytask.shared import to_list


def run_r_script(depends_on, r):
    script = to_list(depends_on)[0]
    subprocess.run(["Rscript", script.as_posix(), *r])


@pytask.hookimpl
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
        r_function.pytestmark = copy.deepcopy(task.function.pytestmark)

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
    args = get_markers_from_task(task, "r")[0].args
    if args:
        out = list(args)
    else:
        out = ["--vanilla"]

    return out
