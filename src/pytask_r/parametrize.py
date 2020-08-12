from _pytask.config import hookimpl
from _pytask.mark import MARK_GEN as mark  # noqa: N811


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    if callable(obj):
        if "r" in kwargs:
            mark.r(*kwargs.pop("r"))(obj)
