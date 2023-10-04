"""Collect tasks."""
from __future__ import annotations

import functools
import subprocess
from pathlib import Path
from types import FunctionType
from typing import Any
import warnings

from pytask import NodeInfo, PTask, PathNode, TaskWithoutPath, depends_on, is_task_function, parse_dependencies_from_task_function, parse_products_from_task_function
from pytask import has_mark
from pytask import hookimpl
from pytask import Mark
from pytask import remove_marks
from pytask import Session
from pytask import Task
from pytask_r.serialization import SERIALIZERS
from pytask_r.shared import r
from pytask_r.shared import R_SCRIPT_KEY


def run_r_script(script: Path, options: list[str], serialized: Path, **kwargs: Any) -> None:
    """Run an R script."""
    cmd = ["Rscript", script.as_posix(), *options, str(serialized)]
    print("Executing " + " ".join(cmd) + ".")  # noqa: T201
    subprocess.run(cmd, check=True)


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
            raise ValueError(
                f"Task {name!r} has multiple @pytask.mark.r marks, but only one is "
                "allowed."
            )

        mark = _parse_r_mark(
            mark=marks[0],
            default_options=session.config["r_options"],
            default_serializer=session.config["r_serializer"],
            default_suffix=session.config["r_suffix"],
        )
        script, options, _, _ = r(**marks[0].kwargs)

        obj.pytask_meta.markers.append(mark)

        # Collect the nodes in @pytask.mark.julia and validate them.
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
                arg_name="script", path=(), value=script, task_path=path, task_name=name
            ),
        )

        if not (isinstance(script_node, PathNode) and script_node.path.suffix == ".r"):
            raise ValueError(
                "The 'script' keyword of the @pytask.mark.r decorator must point "
                f"to Julia file with the .r suffix, but it is {script_node}."
            )


        dependencies = parse_dependencies_from_task_function(
            session, path, name, path_nodes, obj
        )
        products = parse_products_from_task_function(
            session, path, name, path_nodes, obj
        )

        # Add script
        dependencies[R_SCRIPT_KEY] = script_node

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []

        task_function = functools.partial(
            run_r_script,
            script=script_node.path,
            options=options
        )

        if path is None:
            task = TaskWithoutPath(
                name=name,
                function=task_function,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )
        else:
            task = Task(
                base_name=name,
                path=path,
                function=task_function,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )

        return task
    return None


def _parse_r_mark(
    mark: Mark,
    default_options: list[str] | None,
    default_serializer: str,
    default_suffix: str,
) -> Mark:
    """Parse a Julia mark."""
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

    mark = Mark("r", (), parsed_kwargs)
    return mark
