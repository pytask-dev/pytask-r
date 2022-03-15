"""Execute tasks."""
from __future__ import annotations

import shutil

from pytask import has_mark
from pytask import hookimpl


@hookimpl
def pytask_execute_task_setup(task):
    """Perform some checks when a task marked with the r marker is executed."""
    if has_mark(task, "r"):
        if shutil.which("Rscript") is None:
            raise RuntimeError(
                "Rscript is needed to run R scripts, but it is not found on your PATH."
            )
