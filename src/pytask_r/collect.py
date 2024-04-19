"""Collect tasks."""

from __future__ import annotations

import subprocess
import warnings
from pathlib import Path
from typing import Any

from pytask import Mark
from pytask import NodeInfo
from pytask import PathNode
from pytask import PTask
from pytask import PythonNode
from pytask import Session
from pytask import Task
from pytask import TaskWithoutPath
from pytask import has_mark
from pytask import hookimpl
from pytask import is_task_function
from pytask import parse_dependencies_from_task_function
from pytask import parse_products_from_task_function
from pytask import remove_marks

from pytask_r.serialization import SERIALIZERS
from pytask_r.serialization import create_path_to_serialized
from pytask_r.shared import r


def run_r_script(
    _script: Path,
    _options: list[str],
    _serialized: Path,
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Run an R script."""
    cmd = ["Rscript", _script.as_posix(), *_options, str(_serialized)]
    print("Executing " + " ".join(cmd) + ".")  # noqa: T201
    subprocess.run(cmd, check=True)  # noqa: S603


@hookimpl
def pytask_collect_task(
    session: Session, path: Path | None, name: str, obj: Any
) -> PTask | None:
    """Perform some checks."""
    __tracebackhide__ = True

    if (
        (name.startswith("task_") or has_mark(obj, "task"))
        and is_task_function(obj)
        and has_mark(obj, "r")
    ):
        # Parse @pytask.mark.r decorator.
        obj, marks = remove_marks(obj, "r")
        if len(marks) > 1:
            msg = (
                f"Task {name!r} has multiple @pytask.mark.r marks, but only one is "
                "allowed."
            )
            raise ValueError(msg)

        mark = _parse_r_mark(
            mark=marks[0],
            default_options=session.config["r_options"],
            default_serializer=session.config["r_serializer"],
            default_suffix=session.config["r_suffix"],
        )
        script, options, _, suffix = r(**marks[0].kwargs)

        obj.pytask_meta.markers.append(mark)

        # Collect the nodes in @pytask.mark.r and validate them.
        path_nodes = Path.cwd() if path is None else path.parent

        if isinstance(script, str):
            warnings.warn(
                "Passing a string to the @pytask.mark.r parameter 'script' is "
                "deprecated. Please, use a pathlib.Path instead.",
                stacklevel=1,
            )
            script = Path(script)

        script_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="_script",
                path=(),
                value=script,
                task_path=path,
                task_name=name,
            ),
        )

        if not (
            isinstance(script_node, PathNode)
            and script_node.path.suffix in (".r", ".R")
        ):
            msg = (
                "The 'script' keyword of the @pytask.mark.r decorator must point "
                f"to an R file with the .r or .R extension, but it is {script_node}."
            )
            raise ValueError(msg)

        options_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="_options",
                path=(),
                value=options,
                task_path=path,
                task_name=name,
            ),
        )

        dependencies = parse_dependencies_from_task_function(
            session, path, name, path_nodes, obj
        )
        products = parse_products_from_task_function(
            session, path, name, path_nodes, obj
        )

        # Add script
        dependencies["_script"] = script_node
        dependencies["_options"] = options_node

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []

        task: PTask
        if path is None:
            task = TaskWithoutPath(
                name=name,
                function=run_r_script,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )
        else:
            task = Task(
                base_name=name,
                path=path,
                function=run_r_script,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )

        # Add serialized node that depends on the task id.
        serialized = create_path_to_serialized(task, suffix)  # type: ignore[arg-type]
        serialized_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="_serialized",
                path=(),
                value=PythonNode(value=serialized),
                task_path=path,
                task_name=name,
            ),
        )
        task.depends_on["_serialized"] = serialized_node

        return task
    return None


def _parse_r_mark(
    mark: Mark,
    default_options: list[str] | None,
    default_serializer: str,
    default_suffix: str,
) -> Mark:
    """Parse an R mark."""
    script, options, serializer, suffix = r(**mark.kwargs)

    parsed_kwargs = {}
    for arg_name, value, default in (
        ("script", script, None),
        ("options", options, default_options),
        ("serializer", serializer, default_serializer),
    ):
        parsed_kwargs[arg_name] = value or default

    proposed_suffix = (
        SERIALIZERS[parsed_kwargs["serializer"]]["suffix"]
        if isinstance(parsed_kwargs["serializer"], str)
        and parsed_kwargs["serializer"] in SERIALIZERS
        else default_suffix
    )
    parsed_kwargs["suffix"] = suffix or proposed_suffix  # type: ignore[assignment]

    return Mark("r", (), parsed_kwargs)
