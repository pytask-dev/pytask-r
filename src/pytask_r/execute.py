"""Execute tasks."""
from __future__ import annotations

import functools
import shutil
from typing import Any

from pybaum.tree_util import tree_map
from pytask import PPathNode, get_marks
from pytask import hookimpl
from pytask import Task
from pytask_r.serialization import create_path_to_serialized
from pytask_r.serialization import serialize_keyword_arguments
from pytask_r.shared import r
from pytask_r.shared import R_SCRIPT_KEY


@hookimpl
def pytask_execute_task_setup(task: Task) -> None:
    """Perform some checks when a task marked with the r marker is executed."""
    marks = get_marks(task, "r")
    if marks:
        if shutil.which("Rscript") is None:
            raise RuntimeError(
                "Rscript is needed to run R scripts, but it is not found on your PATH."
            )

        assert len(marks) == 1

        _, _, serializer, suffix = r(**marks[0].kwargs)

        path_to_serialized = create_path_to_serialized(task, suffix)
        path_to_serialized.parent.mkdir(parents=True, exist_ok=True)
        task.function = functools.partial(
            task.function,
            serialized=path_to_serialized,
        )
        kwargs = collect_keyword_arguments(task)
        serialize_keyword_arguments(serializer, path_to_serialized, kwargs)


def collect_keyword_arguments(task: Task) -> dict[str, Any]:
    """Collect keyword arguments for function."""
    # Remove all kwargs from the task so that they are not passed to the function.
    kwargs = {
        **tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.depends_on,
        ),
        **tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.produces,
        ),
    }
    kwargs.pop(R_SCRIPT_KEY)
    return kwargs
