from __future__ import annotations

import textwrap

import pytest
from pytask import ExitCode
from pytask import cli

from tests.conftest import needs_rscript
from tests.conftest import parametrize_parse_code_serializer_suffix


@needs_rscript
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_parametrized_execution_of_r_script_w_loop(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask

    for i in range(2):

        @pytask.mark.task
        @pytask.mark.r(
            script=f"script_{{i + 1}}.r",
            serializer="{serializer}",
            suffix="{suffix}"
        )
        @pytask.mark.produces(f"{{i}}.txt")
        def task_run_r_script():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    for name, content in (
        ("script_1.r", "Cities breaking down on a camel's back"),
        ("script_2.r", "They just have to go 'cause they don't know whack"),
    ):
        r_script = f"""
        {parse_config_code}
        file_descr <- file(config$produces)
        writeLines(c("{content}"), file_descr)
        close(file_descr)
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("0.txt").exists()
    assert tmp_path.joinpath("1.txt").exists()


@needs_rscript
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_parametrize_r_options_and_product_paths_w_loop(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask

    for i in range(2):

        @pytask.mark.task
        @pytask.mark.r(
            script=f"script.r",
            serializer="{serializer}",
            suffix="{suffix}"
        )
        @pytask.mark.produces(f"{{i}}.rds")
        def execute_r_script():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = f"""
    {parse_config_code}
    saveRDS(config$number, file=config$produces)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("0.rds").exists()
    assert tmp_path.joinpath("1.rds").exists()
