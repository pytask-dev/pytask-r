"""Configure pytask."""
from __future__ import annotations

from typing import Any

from pytask import hookimpl
from pytask_r.serialization import SERIALIZERS


@hookimpl
def pytask_parse_config(config: dict[str, Any]) -> None:
    """Register the r marker."""
    config["markers"]["r"] = "Tasks which are executed with Rscript."
    config["r_serializer"] = config.get("r_serializer", "json")
    if config["r_serializer"] not in SERIALIZERS:
        raise ValueError(
            f"'r_serializer' is {config['r_serializer']} and not one of "
            f"{list(SERIALIZERS)}."
        )
    config["r_suffix"] = config.get("r_suffix", "")
    config["r_options"] = _parse_value_or_whitespace_option(config.get("r_options"))


def _parse_value_or_whitespace_option(value: Any) -> list[str] | None:
    """Parse option which can hold a single value or values separated by new lines."""
    if value is None:
        return None
    if isinstance(value, list):
        return list(map(str, value))
    raise ValueError(f"'r_options' is {value} and not a list.")
