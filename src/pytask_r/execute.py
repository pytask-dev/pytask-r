"""Execute tasks."""
import shutil

from _pytask.config import hookimpl
from _pytask.mark import get_specific_markers_from_task


@hookimpl
def pytask_execute_task_setup(task):
    """Perform some checks when a task marked with the r marker is executed."""
    if get_specific_markers_from_task(task, "r"):
        if shutil.which("Rscript") is None:
            raise RuntimeError(
                "Rscript is needed to run R scripts, but it is not found on your PATH."
            )
