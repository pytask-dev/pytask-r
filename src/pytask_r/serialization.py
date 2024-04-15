"""This module contains the code to serialize keyword arguments to the task."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from typing import Callable

from pytask import PTask
from pytask import PTaskWithPath


_HIDDEN_FOLDER = ".pytask/pytask-r"


SERIALIZERS = {"json": {"serializer": json.dumps, "suffix": ".json"}}


try:
    import yaml
except ImportError:  # pragma: no cover
    pass
else:
    SERIALIZERS["yaml"] = {"serializer": yaml.dump, "suffix": ".yaml"}
    SERIALIZERS["yml"] = {"serializer": yaml.dump, "suffix": ".yml"}


def create_path_to_serialized(task: PTask, suffix: str) -> Path:
    """Create path to serialized."""
    parent = task.path.parent if isinstance(task, PTaskWithPath) else Path.cwd()
    file_name = create_file_name(task, suffix)
    path = parent.joinpath(_HIDDEN_FOLDER, file_name).with_suffix(suffix)
    return path


def create_file_name(task: PTask, suffix: str) -> str:
    """Create the file name of the file containing the serialized kwargs.

    Some characters need to be escaped since they are not valid characters on file
    systems.

    """
    return (
        task.name.replace("[", "_")
        .replace("]", "_")
        .replace("::", "_")
        .replace(".", "_")
        .replace("/", "_")
        + suffix
    )


def serialize_keyword_arguments(
    serializer: str | Callable[..., str],
    path_to_serialized: Path,
    kwargs: dict[str, Any],
) -> None:
    """Serialize keyword arguments."""
    if callable(serializer):
        serializer_func = serializer
    elif isinstance(serializer, str) and serializer in SERIALIZERS:
        serializer_func = SERIALIZERS[serializer][
            "serializer"
        ]  # type: ignore[assignment]
    else:
        raise ValueError(f"Serializer {serializer!r} is not known.")

    serialized = serializer_func(kwargs)
    path_to_serialized.write_text(serialized)
