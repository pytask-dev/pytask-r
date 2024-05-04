from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from pytask import ExitCode
from pytask import Mark
from pytask import Task
from pytask import build
from pytask import cli
from pytask_r.execute import pytask_execute_task_setup

from tests.conftest import needs_rscript
from tests.conftest import parametrize_parse_code_serializer_suffix


@pytest.mark.unit()
def test_pytask_execute_task_setup(monkeypatch):
    """Make sure that the task setup raises errors."""
    # Act like r is installed since we do not test this.
    monkeypatch.setattr("pytask_r.execute.shutil.which", lambda x: None)  # noqa: ARG005

    task = Task(
        base_name="task_example",
        path=Path(),
        function=None,
        markers=[Mark("r", (), {})],
    )

    with pytest.raises(RuntimeError, match="Rscript is needed"):
        pytask_execute_task_setup(task)


@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
@pytest.mark.parametrize("depends_on", ["'in_1.txt'", "['in_1.txt', 'in_2.txt']"])
def test_run_r_script(  # noqa: PLR0913
    runner, tmp_path, parse_config_code, serializer, suffix, depends_on
):
    task_source = f"""
    from pathlib import Path
    from pytask import mark

    @mark.r(script="script.r", serializer="{serializer}", suffix="{suffix}")
    @mark.depends_on({depends_on})
    def task_run_r_script(produces = Path("out.txt")): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("in_1.txt").touch()
    tmp_path.joinpath("in_2.txt").touch()

    r_script = f"""
    {parse_config_code}
    if(length(config["depends_on"]) <= 0){{
       stop("error message to print")  # noqa: T201
    }}
    file_descriptor <- file(config$produces)
    writeLines(c("So, so you think you can tell heaven from hell?"), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    print(result.output)  # noqa: T201
    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
def test_run_r_script_w_task_decorator(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    task_source = f"""
    from pytask import task, mark

    @task
    @mark.r(script="script.r", serializer="{serializer}", suffix="{suffix}")
    @mark.produces("out.txt")
    def run_r_script(): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = f"""
    {parse_config_code}
    file_descriptor <- file(config$produces)
    writeLines(c("So, so you think you can tell heaven from hell?"), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
def test_raise_error_if_rscript_is_not_found(
    tmp_path, monkeypatch, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask

    @pytask.mark.r(script="script.r", serializer="{serializer}", suffix="{suffix}")
    @pytask.mark.produces("out.txt")
    def task_run_r_script(): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = f"""
    {parse_config_code}
    file_descr <- file(config$produces)
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    # Hide Rscript if available.
    monkeypatch.setattr("pytask_r.execute.shutil.which", lambda x: None)  # noqa: ARG005

    session = build(paths=tmp_path)

    assert session.exit_code == ExitCode.FAILED
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
def test_run_r_script_w_saving_workspace(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Save workspace while executing the script."""
    task_source = f"""
    import pytask

    @pytask.mark.r(
        script="script.r",
        options="--save",
        serializer="{serializer}",
        suffix="{suffix}"
    )
    @pytask.mark.produces("out.txt")
    def task_run_r_script(): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = f"""
    {parse_config_code}
    file_descr <- file(config$produces)
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
def test_run_r_script_w_wrong_cmd_option(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Save workspace while executing the script."""
    task_source = f"""
    import pytask

    @pytask.mark.r(
        script="script.r",
        options="--wrong-flag",
        serializer="{serializer}",
        suffix="{suffix}"
    )
    @pytask.mark.produces("out.txt")
    def task_run_r_script(): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = f"""
    {parse_config_code}
    file_descr <- file(config$produces)
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end()
def test_run_r_script_w_custom_serializer(runner, tmp_path):
    task_source = """
    import pytask
    import json

    @pytask.mark.r(script="script.r", serializer=json.dumps, suffix=".json")
    @pytask.mark.produces("out.txt")
    def task_run_r_script(): ...

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = """
    library(jsonlite)
    args <- commandArgs(trailingOnly=TRUE)
    config <- read_json(args[length(args)])
    file_descriptor <- file(config$produces)
    writeLines(c("So, so you think you can tell heaven from hell?"), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end()
def test_run_r_script_fails_w_multiple_markers(runner, tmp_path):
    task_source = """
    import pytask

    @pytask.mark.r(script="script.r")
    @pytask.mark.r(script="script.r")
    @pytask.mark.produces("out.txt")
    def task_run_r_script(): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("script.r").touch()

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert "has multiple @pytask.mark.r marks" in result.output


@needs_rscript
@pytest.mark.end_to_end()
def test_run_r_script_with_capital_extension(runner, tmp_path):
    task_source = """
    import pytask

    @pytask.mark.r(script="script.R")
    @pytask.mark.produces("out.txt")
    def task_run_r_script(): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = """
    library(jsonlite)
    args <- commandArgs(trailingOnly=TRUE)
    config <- read_json(args[length(args)])
    file_descriptor <- file(config$produces)
    writeLines(c("So, so you think you can tell heaven from hell?"), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.R").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end()
@parametrize_parse_code_serializer_suffix
def test_run_r_script_w_nested_inputs(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    task_source = f"""
    from pytask import mark, task

    @task(kwargs={{"content": {{"first": "Hello, ", "second": "World!"}}}})
    @mark.r(script="script.r", serializer="{serializer}", suffix="{suffix}")
    @mark.produces("out.txt")
    def task_run_r_script(): ...
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = f"""
    {parse_config_code}
    file_descriptor <- file(config$produces)
    writeLines(c(config$content$first, config$content$second), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").read_text() == "Hello, \nWorld!\n"
