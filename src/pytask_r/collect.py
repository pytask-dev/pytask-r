"""Collect tasks."""
from __future__ import annotations

import functools
import subprocess
from pathlib import Path
from types import FunctionType
from typing import Any

from pytask import depends_on
from pytask import has_mark
from pytask import hookimpl
from pytask import Mark
from pytask import parse_nodes
from pytask import produces
from pytask import remove_marks
from pytask import Session
from pytask import Task
from pytask_r.serialization import SERIALIZERS
from pytask_r.shared import r
from pytask_r.shared import R_SCRIPT_KEY


def run_r_script(script: Path, options: list[str], serialized: Path) -> None:
    """Run an R script."""
    cmd = ["Rscript", script.as_posix(), *options, str(serialized)]
    print("Executing " + " ".join(cmd) + ".")  # noqa: T201
    subprocess.run(cmd, check=True)


@hookimpl
def pytask_collect_task(
    session: Session, path: Path, name: str, obj: Any
) -> Task | None:
    """Perform some checks."""
    __tracebackhide__ = True

    if (
        (name.startswith("task_") or has_mark(obj, "task"))
        and callable(obj)
        and has_mark(obj, "r")
    ):
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

        dependencies = parse_nodes(session, path, name, obj, depends_on)
        products = parse_nodes(session, path, name, obj, produces)

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []
        kwargs = obj.pytask_meta.kwargs if hasattr(obj, "pytask_meta") else {}

        task = Task(
            base_name=name,
            path=path,
            function=_copy_func(run_r_script),  # type: ignore[arg-type]
            depends_on=dependencies,
            produces=products,
            markers=markers,
            kwargs=kwargs,
        )

        script_node = session.hook.pytask_collect_node(
            session=session, path=path, node=script
        )

        if isinstance(task.depends_on, dict):
            task.depends_on[R_SCRIPT_KEY] = script_node
            task.attributes["r_keep_dict"] = True
        else:
            task.depends_on = {0: task.depends_on, R_SCRIPT_KEY: script_node}
            task.attributes["r_keep_dict"] = False

        task.function = functools.partial(
            task.function, script=task.depends_on[R_SCRIPT_KEY].path, options=options
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


def _copy_func(func: FunctionType) -> FunctionType:
    """Create a copy of a function.

    Based on https://stackoverflow.com/a/13503277/7523785.

    Example
    -------
    >>> def _func(): pass
    >>> copied_func = _copy_func(_func)
    >>> _func is copied_func
    False

    """
    new_func = FunctionType(
        func.__code__,
        func.__globals__,
        name=func.__name__,
        argdefs=func.__defaults__,
        closure=func.__closure__,
    )
    new_func = functools.update_wrapper(new_func, func)
    new_func.__kwdefaults__ = func.__kwdefaults__
    return new_func
