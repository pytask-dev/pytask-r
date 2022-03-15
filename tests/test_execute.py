from __future__ import annotations

import os
import textwrap
from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from conftest import needs_rscript
from pytask import ExitCode
from pytask import main
from pytask import Mark
from pytask import Task
from pytask_r.execute import pytask_execute_task_setup


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "found_r, expectation",
    [
        (True, does_not_raise()),
        (None, pytest.raises(RuntimeError)),
    ],
)
def test_pytask_execute_task_setup(monkeypatch, found_r, expectation):
    """Make sure that the task setup raises errors."""
    # Act like r is installed since we do not test this.
    monkeypatch.setattr(
        "pytask_r.execute.shutil.which", lambda x: found_r  # noqa: U100
    )

    task = Task(
        base_name="task_example",
        path=Path(),
        function=None,
        markers=[Mark("r", (), {})],
    )

    with expectation:
        pytask_execute_task_setup(task)


@needs_rscript
@pytest.mark.end_to_end
@pytest.mark.parametrize(
    "depends_on",
    ["'script.r'", {"source": "script.r"}, {0: "script.r"}, {"script": "script.r"}],
)
def test_run_r_script(tmp_path, depends_on):
    task_source = f"""
    import pytask

    @pytask.mark.r
    @pytask.mark.depends_on({depends_on})
    @pytask.mark.produces("out.txt")
    def task_run_r_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = """
    file_descriptor <- file("out.txt")
    writeLines(c("So, so you think you can tell heaven from hell?"), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    if (
        isinstance(depends_on, dict)
        and "source" not in depends_on
        and 0 not in depends_on
    ):
        tmp_path.joinpath("pytask.ini").write_text("[pytask]\nr_source_key = script")

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@pytest.mark.end_to_end
def test_raise_error_if_rscript_is_not_found(tmp_path, monkeypatch):
    task_source = """
    import pytask

    @pytask.mark.r
    @pytask.mark.depends_on("script.r")
    @pytask.mark.produces("out.txt")
    def task_run_r_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = """
    file_descr <- file("out.txt")
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    # Hide Rscript if available.
    monkeypatch.setattr("pytask_r.execute.shutil.which", lambda x: None)  # noqa: U100

    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.FAILED
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_rscript
@pytest.mark.end_to_end
def test_run_r_script_w_saving_workspace(tmp_path):
    """Save workspace while executing the script."""
    task_source = """
    import pytask

    @pytask.mark.r("--save")
    @pytask.mark.depends_on("script.r")
    @pytask.mark.produces("out.txt")
    def task_run_r_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = """
    file_descr <- file("out.txt")
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end
def test_run_r_script_w_wrong_cmd_option(tmp_path):
    """Apparently, Rscript simply discards wrong cmd options."""
    task_source = """
    import pytask

    @pytask.mark.r("--wrong-flag")
    @pytask.mark.depends_on("script.r")
    @pytask.mark.produces("out.txt")
    def task_run_r_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = """
    file_descr <- file("out.txt")
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == ExitCode.OK
