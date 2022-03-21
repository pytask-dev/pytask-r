"""Configure pytask."""
from __future__ import annotations

from pytask import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the r marker."""
    config["markers"]["r"] = "Tasks which are executed with Rscript."
    config["r_serializer"] = config_from_file.get("r_serializer", "json")
    config["r_suffix"] = config_from_file.get("r_suffix", "")
    options = config_from_file.get("r_options")
    config["r_options"] = options.split(" ") if isinstance(options, str) else []
