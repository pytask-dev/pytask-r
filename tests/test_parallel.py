"""Contains test which ensure that the plugin works with pytask-parallel."""
from __future__ import annotations

import textwrap
import time

import pytest
from pytask import cli
from pytask import ExitCode

from tests.conftest import needs_rscript, parametrize_parse_code_serializer_suffix

try:
    import pytask_parallel  # noqa: F401
except ImportError:
    _IS_PYTASK_PARALLEL_INSTALLED = False
else:
    _IS_PYTASK_PARALLEL_INSTALLED = True


pytestmark = pytest.mark.skipif(
    not _IS_PYTASK_PARALLEL_INSTALLED, reason="Tests require pytask-parallel."
)


@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
def test_parallel_parametrization_over_source_files_w_loop(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Test parallelization over source files.

    Same as in README.md.

    """
    source = f"""
    import pytask

    for i in range(1, 3):

        @pytask.mark.task(kwargs={{"content": i}})
        @pytask.mark.r(
            script="script_1.r",
            serializer="{serializer}",
            suffix="{suffix}"
        )
        @pytask.mark.produces(f"{{i}}.rds")
        def task_execute_r_script():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    r_script = f"""
    {parse_config_code}
    saveRDS(config$content, file=config$produces)
    """
    tmp_path.joinpath("script_1.r").write_text(textwrap.dedent(r_script))

    r_script = f"""
    {parse_config_code}
    saveRDS(config$content, file=config$produces)
    """
    tmp_path.joinpath("script_2.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == ExitCode.OK



@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
def test_parallel_parametrization_over_source_file_w_loop(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Test parallelization over the same source file.

    Same as in README.md.

    """
    source = f"""
    import pytask

    for i in range(2):

        @pytask.mark.task(kwargs={{"content": i}})
        @pytask.mark.r(
            script="script.r",
            serializer="{serializer}",
            suffix="{suffix}",
        )
        @pytask.mark.produces(f"{{i}}.rds")
        def execute_r_script():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    r_script = f"""
    {parse_config_code}
    saveRDS(config$content, file=config$produces)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == ExitCode.OK
