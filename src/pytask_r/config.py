"""Configure pytask."""
from __future__ import annotations

from pytask import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the r marker."""
    config["markers"]["r"] = "Tasks which are executed with Rscript."
    config["r_serializer"] = config_from_file.get("r_serializer", "json")
    config["r_suffix"] = config_from_file.get("r_suffix", "")
    config["r_options"] = _parse_value_or_whitespace_option(
        config_from_file.get("r_options")
    )


def _parse_value_or_whitespace_option(value: str | None) -> None | str | list[str]:
    """Parse option which can hold a single value or values separated by new lines."""
    if value in ["none", "None", None, ""]:
        return None
    elif isinstance(value, list):
        return list(map(str, value))
    elif isinstance(value, str):
        return [v.strip() for v in value.split(" ") if v.strip()]
    else:
        raise ValueError(f"Input {value!r} is neither a 'str' nor 'None'.")
