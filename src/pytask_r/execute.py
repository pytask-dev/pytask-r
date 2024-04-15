"""Execute tasks."""

from __future__ import annotations

import shutil
from typing import Any

from pytask import get_marks
from pytask import hookimpl
from pytask import PPathNode
from pytask import PTask
from pytask import PythonNode
from pytask.tree_util import tree_map
from pytask_r.serialization import serialize_keyword_arguments
from pytask_r.shared import r


@hookimpl
def pytask_execute_task_setup(task: PTask) -> None:
    """Perform some checks when a task marked with the r marker is executed."""
    marks = get_marks(task, "r")
    if marks:
        if shutil.which("Rscript") is None:
            raise RuntimeError(
                "Rscript is needed to run R scripts, but it is not found on your PATH."
            )

        assert len(marks) == 1

        _, _, serializer, suffix = r(**marks[0].kwargs)
        assert serializer
        assert suffix

        serialized_node: PythonNode = task.depends_on["_serialized"]  # type: ignore[assignment]
        serialized_node.value.parent.mkdir(parents=True, exist_ok=True)
        kwargs = collect_keyword_arguments(task)
        serialize_keyword_arguments(serializer, serialized_node.value, kwargs)


def collect_keyword_arguments(task: PTask) -> dict[str, Any]:
    """Collect keyword arguments for function."""
    # Remove all kwargs from the task so that they are not passed to the function.
    kwargs: dict[str, Any] = {
        **tree_map(  # type: ignore[dict-item]
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.depends_on,
        ),
        **tree_map(  # type: ignore[dict-item]
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.produces,
        ),
    }
    kwargs.pop("_script")
    kwargs.pop("_options")
    kwargs.pop("_serialized")
    return kwargs
