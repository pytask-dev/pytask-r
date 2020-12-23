from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from _pytask.mark import Mark
from _pytask.nodes import FilePathNode
from pytask_r.collect import _get_node_from_dictionary
from pytask_r.collect import _merge_all_markers
from pytask_r.collect import _prepare_cmd_options
from pytask_r.collect import pytask_collect_task
from pytask_r.collect import pytask_collect_task_teardown
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
    "name, expected",
    [("task_dummy", True), ("invalid_name", None)],
)
def test_pytask_collect_task(name, expected):
    session = DummyClass()
    path = Path("some_path")
    task_dummy.pytaskmark = [Mark("r", (), {})]

    task = pytask_collect_task(session, path, name, task_dummy)

    if expected:
        assert task
    else:
        assert not task


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
@pytest.mark.parametrize("r_source_key", ["source", "script"])
def test_pytask_collect_task_teardown(depends_on, produces, expectation, r_source_key):
    session = DummyClass()
    session.config = {"r_source_key": r_source_key}

    task = DummyClass()
    task.depends_on = {
        i: FilePathNode.from_path(Path(n)) for i, n in enumerate(depends_on)
    }
    task.produces = {i: FilePathNode.from_path(Path(n)) for i, n in enumerate(produces)}
    task.markers = [Mark("r", (), {})]
    task.function = task_dummy
    task.function.pytaskmark = task.markers

    with expectation:
        pytask_collect_task_teardown(session, task)


@pytest.mark.unit
@pytest.mark.parametrize(
    "obj, key, expected",
    [
        (1, "asds", 1),
        (1, None, 1),
        ({"a": 1}, "a", 1),
        ({0: 1}, "a", 1),
    ],
)
def test_get_node_from_dictionary(obj, key, expected):
    result = _get_node_from_dictionary(obj, key)
    assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "args",
    [
        [],
        ["a"],
        ["a", "b"],
    ],
)
@pytest.mark.parametrize("r_source_key", ["source", "script"])
def test_prepare_cmd_options(args, r_source_key):
    session = DummyClass()
    session.config = {"r_source_key": r_source_key}

    node = DummyClass()
    node.value = Path("script.r")
    task = DummyClass()
    task.depends_on = {r_source_key: node}
    task.name = "task"

    result = _prepare_cmd_options(session, task, args)

    assert result == ["Rscript", "script.r", *args]
