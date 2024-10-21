from __future__ import annotations

from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from pytask import Mark

from pytask_r.collect import _parse_r_mark
from pytask_r.collect import r
from pytask_r.serialization import SERIALIZERS


@pytest.mark.unit
@pytest.mark.parametrize(
    ("args", "kwargs", "expectation", "expected"),
    [
        (
            (),
            {
                "script": "script.r",
                "options": "--option",
                "serializer": "json",
                "suffix": ".json",
            },
            does_not_raise(),
            ("script.r", ["--option"], "json", ".json"),
        ),
        (
            (),
            {
                "script": "script.r",
                "options": [1],
                "serializer": "yaml",
                "suffix": ".yaml",
            },
            does_not_raise(),
            ("script.r", ["1"], "yaml", ".yaml"),
        ),
    ],
)
def test_r(args, kwargs, expectation, expected):
    with expectation:
        result = r(*args, **kwargs)
        assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    (
        "mark",
        "default_options",
        "default_serializer",
        "default_suffix",
        "expectation",
        "expected",
    ),
    [
        (
            Mark("r", (), {"script": "script.r"}),
            [],
            None,
            ".json",
            does_not_raise(),
            Mark(
                "r",
                (),
                {
                    "script": "script.r",
                    "options": [],
                    "serializer": None,
                    "suffix": ".json",
                },
            ),
        ),
        (
            Mark(
                "r",
                (),
                {
                    "script": "script.r",
                    "serializer": "json",
                },
            ),
            [],
            None,
            None,
            does_not_raise(),
            Mark(
                "r",
                (),
                {
                    "script": "script.r",
                    "options": [],
                    "serializer": "json",
                    "suffix": SERIALIZERS["json"]["suffix"],
                },
            ),
        ),
    ],
)
def test_parse_r_mark(  # noqa: PLR0913
    mark,
    default_options,
    default_serializer,
    default_suffix,
    expectation,
    expected,
):
    with expectation:
        out = _parse_r_mark(mark, default_options, default_serializer, default_suffix)
        assert out == expected
