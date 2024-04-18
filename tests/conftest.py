from __future__ import annotations

import shutil
import sys
from contextlib import contextmanager
from typing import Callable

import pytest
from click.testing import CliRunner

needs_rscript = pytest.mark.skipif(
    shutil.which("Rscript") is None, reason="R with Rscript needs to be installed."
)


parametrize_parse_code_serializer_suffix = pytest.mark.parametrize(
    "parse_config_code, serializer, suffix",
    [
        (
            "library(jsonlite); args <- commandArgs(trailingOnly=TRUE); "
            "config <- read_json(args[length(args)])",
            "json",
            ".json",
        ),
        (
            "library(yaml); args <- commandArgs(trailingOnly=TRUE); "
            "config <- read_yaml(args[length(args)])",
            "yaml",
            ".yaml",
        ),
    ],
)


class SysPathsSnapshot:
    """A snapshot for sys.path."""

    def __init__(self) -> None:
        self.__saved = sys.path.copy(), sys.meta_path.copy()

    def restore(self) -> None:
        sys.path[:], sys.meta_path[:] = self.__saved


class SysModulesSnapshot:
    """A snapshot for sys.modules."""

    def __init__(self, preserve: Callable[[str], bool] | None = None) -> None:
        self.__preserve = preserve
        self.__saved = sys.modules.copy()

    def restore(self) -> None:
        if self.__preserve:
            self.__saved.update(
                (k, m) for k, m in sys.modules.items() if self.__preserve(k)
            )
        sys.modules.clear()
        sys.modules.update(self.__saved)


@contextmanager
def restore_sys_path_and_module_after_test_execution():
    sys_path_snapshot = SysPathsSnapshot()
    sys_modules_snapshot = SysModulesSnapshot()
    yield
    sys_modules_snapshot.restore()
    sys_path_snapshot.restore()


@pytest.fixture(autouse=True)
def _restore_sys_path_and_module_after_test_execution():
    """Restore sys.path and sys.modules after every test execution.

    This fixture became necessary because most task modules in the tests are named
    `task_example`. Since the change in #424, the same module is not reimported which
    solves errors with parallelization. At the same time, modules with the same name in
    the tests are overshadowing another and letting tests fail.

    The changes to `sys.path` might not be necessary to restore, but we do it anyways.

    """
    with restore_sys_path_and_module_after_test_execution():
        yield


class CustomCliRunner(CliRunner):
    def invoke(self, *args, **kwargs):
        """Restore sys.path and sys.modules after an invocation."""
        with restore_sys_path_and_module_after_test_execution():
            return super().invoke(*args, **kwargs)


@pytest.fixture()
def runner():
    return CustomCliRunner()
