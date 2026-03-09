"""Contains the code to serialize keyword arguments to the task."""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any
from typing import TypedDict
from typing import cast

from pytask import PTask
from pytask import PTaskWithPath

__all__ = ["SERIALIZERS", "create_path_to_serialized", "serialize_keyword_arguments"]

_HIDDEN_FOLDER = ".pytask/pytask-r"


SerializerFunc = Callable[..., str]


class SerializerEntry(TypedDict):
    """Describe a serializer function and its output suffix."""

    serializer: SerializerFunc
    suffix: str


SERIALIZERS: dict[str, SerializerEntry] = {
    "json": {"serializer": json.dumps, "suffix": ".json"}
}


try:
    import yaml
except ImportError:  # pragma: no cover
    pass
else:
    yaml_dump = cast("SerializerFunc", yaml.dump)
    SERIALIZERS["yaml"] = {"serializer": yaml_dump, "suffix": ".yaml"}
    SERIALIZERS["yml"] = {"serializer": yaml_dump, "suffix": ".yml"}


def create_path_to_serialized(task: PTask, suffix: str) -> Path:
    """Create path to serialized."""
    return (
        (task.path.parent if isinstance(task, PTaskWithPath) else Path.cwd())
        .joinpath(_HIDDEN_FOLDER, str(uuid.uuid4()))
        .with_suffix(suffix)
    )


def serialize_keyword_arguments(
    serializer: str | SerializerFunc,
    path_to_serialized: Path,
    kwargs: dict[str, Any],
) -> None:
    """Serialize keyword arguments."""
    if isinstance(serializer, str):
        if serializer not in SERIALIZERS:
            msg = f"Serializer {serializer!r} is not known."
            raise ValueError(msg)
        serializer_func = SERIALIZERS[serializer]["serializer"]
    elif callable(serializer):
        serializer_func = serializer
    else:
        msg = f"Serializer {serializer!r} is not known."
        raise TypeError(msg)

    serialized = serializer_func(kwargs)
    path_to_serialized.write_text(serialized)
