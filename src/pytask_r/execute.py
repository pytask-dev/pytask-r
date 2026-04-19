"""Execute tasks."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from pytask import PPathNode
from pytask import PTask
from pytask import PythonNode
from pytask import get_marks
from pytask import hookimpl
from pytask.tree_util import tree_map

from pytask_r.serialization import serialize_keyword_arguments
from pytask_r.shared import r

if TYPE_CHECKING:
    from pathlib import Path


@hookimpl
def pytask_execute_task_setup(task: PTask) -> None:
    """Perform some checks when a task marked with the r marker is executed."""
    marks = get_marks(task, "r")
    if marks:
        if shutil.which("Rscript") is None:
            msg = (
                "Rscript is needed to run R scripts, but it is not found on your PATH."
            )
            raise RuntimeError(msg)

        if len(marks) > 1:
            msg = "Only one R marker is allowed per task."
            raise ValueError(msg)

        _, _, serializer, _ = r(**marks[0].kwargs)
        if serializer is None:  # pragma: no cover
            msg = "Missing serializer for R task."
            raise ValueError(msg)

        serialized_node = cast("PythonNode", task.depends_on["_serialized"])
        path_to_serialized = cast("Path", serialized_node.value)
        path_to_serialized.parent.mkdir(parents=True, exist_ok=True)
        kwargs = collect_keyword_arguments(task)
        serialize_keyword_arguments(serializer, path_to_serialized, kwargs)


def collect_keyword_arguments(task: PTask) -> dict[str, Any]:
    """Collect keyword arguments for function."""
    # Remove all kwargs from the task so that they are not passed to the function.
    kwargs: dict[str, Any] = {
        **tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else x.value,
            task.depends_on,
        ),
        **tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else x.value,
            task.produces,
        ),
    }
    kwargs.pop("_script")
    kwargs.pop("_options")
    kwargs.pop("_serialized")
    return kwargs
