import pytask


@pytask.hookimpl
def pytask_generate_tasks_add_marker(obj, kwargs):
    if callable(obj):
        if "r" in kwargs:
            pytask.mark.__getattr__("r")(*kwargs.pop("r"))(obj)
