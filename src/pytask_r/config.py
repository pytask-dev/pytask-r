"""Configure pytask."""
from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the r marker."""
    config["markers"]["r"] = "Tasks which are executed with Rscript."
    config["r_source_key"] = config_from_file.get("r_source_key", "source")
