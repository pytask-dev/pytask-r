from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from _pytask.mark import Mark
from _pytask.nodes import FilePathNode
from pytask_r.collect import _merge_all_markers
from pytask_r.collect import pytask_collect_task
from pytask_r.collect import r


class DummyClass:
    pass


def task_dummy():
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "r_args, expected",
    [
        (None, ["--vanilla"]),
        ("--some-option", ["--some-option"]),
        (["--a", "--b"], ["--a", "--b"]),
    ],
)
def test_r(r_args, expected):
    options = r(r_args)
    assert options == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "marks, expected",
    [
        (
            [Mark("r", ("--a",), {}), Mark("r", ("--b",), {})],
            Mark("r", ("--a", "--b"), {}),
        ),
        (
            [Mark("r", ("--a",), {}), Mark("r", (), {"r": "--b"})],
            Mark("r", ("--a",), {"r": "--b"}),
        ),
    ],
)
def test_merge_all_markers(marks, expected):
    task = DummyClass()
    task.markers = marks
    out = _merge_all_markers(task)
    assert out == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "depends_on, produces, expectation",
    [
        (["script.r"], ["any_out.rds"], does_not_raise()),
        (["script.R"], ["any_out.rds"], does_not_raise()),
        (["script.txt"], ["any_out.rds"], pytest.raises(ValueError)),
        (["input.rds", "script.r"], ["any_out.rds"], pytest.raises(ValueError)),
        (["input.rds", "script.R"], ["any_out.rds"], pytest.raises(ValueError)),
    ],
)
def test_pytask_collect_task(monkeypatch, depends_on, produces, expectation):
    session = DummyClass()
    path = Path("some_path")

    task_dummy.pytaskmark = [Mark("r", (), {})] + [
        Mark("depends_on", tuple(d for d in depends_on), {}),
        Mark("produces", tuple(d for d in produces), {}),
    ]

    task = DummyClass()
    task.depends_on = [FilePathNode(n.split(".")[0], Path(n)) for n in depends_on]
    task.produces = [FilePathNode(n.split(".")[0], Path(n)) for n in produces]
    task.markers = [Mark("r", (), {})]
    task.function = task_dummy

    monkeypatch.setattr(
        "pytask_r.collect.PythonFunctionTask.from_path_name_function_session",
        lambda *x: task,
    )

    with expectation:
        pytask_collect_task(session, path, "task_dummy", task_dummy)
