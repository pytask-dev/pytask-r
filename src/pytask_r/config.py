"""Configure pytask."""
from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config):
    """Register the r marker."""
    config["markers"]["r"] = "Tasks which are executed with Rscript."
