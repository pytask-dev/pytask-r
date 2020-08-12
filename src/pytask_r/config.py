from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config):
    config["markers"]["r"] = "r: Tasks which are executed with Rscript."
