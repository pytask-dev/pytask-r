"""Contains the code to serialize keyword arguments to the task."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from pytask import PTask
from pytask import PTaskWithPath

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["SERIALIZERS", "create_path_to_serialized", "serialize_keyword_arguments"]

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
    return (
        (task.path.parent if isinstance(task, PTaskWithPath) else Path.cwd())
        .joinpath(_HIDDEN_FOLDER, str(uuid.uuid4()))
        .with_suffix(suffix)
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
        serializer_func = cast(
            "Callable[..., str]", SERIALIZERS[serializer]["serializer"]
        )
    else:
        msg = f"Serializer {serializer!r} is not known."
        raise ValueError(msg)

    serialized = serializer_func(kwargs)
    path_to_serialized.write_text(serialized)
