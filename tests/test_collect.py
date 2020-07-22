import pytest
from pytask.mark import Mark
from pytask_r.collect import _create_command_line_arguments


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "args, expected", [((), ["--vanilla"]), (("--no-environ",), ["--no-environ"])],
)
def test_create_command_line_arguments(args, expected):
    task = DummyTask()
    task.markers = [Mark("r", args, {})]

    out = _create_command_line_arguments(task)

    assert out == expected
