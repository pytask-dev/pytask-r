"""Execute tasks."""
import shutil

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task
from _pytask.nodes import FilePathNode


@hookimpl
def pytask_execute_task_setup(task):
    """Perform some checks when a task marked with the r marker is executed."""
    if get_specific_markers_from_task(task, "r"):
        if shutil.which("Rscript") is None:
            raise RuntimeError(
                "Rscript is needed to run R scripts, but it is not found on your PATH."
            )

        if not (
            isinstance(task.depends_on[0], FilePathNode)
            and task.depends_on[0].value.suffix in [".r", ".R"]
        ):
            raise ValueError(
                "The first dependency must be a path to an .r or .R script."
            )
