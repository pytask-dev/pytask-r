import shutil

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.nodes import FilePathNode


@hookimpl
def pytask_execute_task_setup(task):
    if get_specific_markers_from_task(task, "r"):
        if shutil.which("Rscript") is None:
            raise RuntimeError(
                "Rscript is needed to run R scripts, but it is not found on your PATH."
            )

        if not (
            isinstance(task.depends_on[0], FilePathNode)
            and task.depends_on[0].value.suffix in [".r", ".R"]
        ):
            raise ValueError("'depends_on' must be a path to a single .r script.")
