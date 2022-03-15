from __future__ import annotations

from pathlib import Path

import pytest
from pytask import Mark
from pytask_r.collect import _get_node_from_dictionary
from pytask_r.collect import _merge_all_markers
from pytask_r.collect import _prepare_cmd_options
from pytask_r.collect import r


class DummyClass:
    pass


def task_dummy():
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "r_args, expected",
    [
        (None, []),
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
    out = _merge_all_markers(marks)
    assert out == expected


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
    node.path = Path("script.r")
    task = DummyClass()
    task.depends_on = {r_source_key: node}
    task.name = "task"

    result = _prepare_cmd_options(session, task, args)

    assert result == ["Rscript", "script.r", *args]
