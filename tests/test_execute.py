import os
import textwrap
from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from conftest import needs_rscript
from pytask.main import main
from pytask.mark import Mark
from pytask.nodes import FilePathNode
from pytask_r.execute import pytask_execute_task_setup


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "depends_on, expectation",
    [
        ([FilePathNode("a", Path("a.r"))], does_not_raise(),),
        (
            [FilePathNode("a", Path("a.txt")), FilePathNode("b", Path("b.r"))],
            pytest.raises(ValueError),
        ),
    ],
)
def test_pytask_execute_task_setup_dependency(monkeypatch, depends_on, expectation):
    # Act like latexmk is installed since we do not test this.
    monkeypatch.setattr("pytask_r.execute.shutil.which", lambda x: True)

    task = DummyTask()
    task.depends_on = depends_on
    task.markers = [Mark("r", (), {})]

    with expectation:
        pytask_execute_task_setup(task)


@needs_rscript
@pytest.mark.end_to_end
def test_run_r_script(tmp_path):
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
    file_descriptor <- file("out.txt")
    writeLines(c("So, so you think you can tell heaven from hell?"), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("out.txt").exists()


@needs_rscript
@pytest.mark.end_to_end
def test_parametrized_execution_of_r_script(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.r
    @pytask.mark.parametrize("depends_on, produces", [
        ("script_1.r", "0.txt"),
        ("script_2.r", "1.txt"),
    ])
    def task_run_r_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    for name, content, out in [
        ("script_1.r", "Cities breaking down on a camel's back", "0.txt"),
        ("script_2.r", "They just have to go 'cause they don't know whack", "1.txt"),
    ]:
        r_script = f"""
        file_descr <- file("{out}")
        writeLines(c("{content}"), file_descr)
        close(file_descr)
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(r_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("0.txt").exists()
    assert tmp_path.joinpath("1.txt").exists()


@needs_rscript
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
    monkeypatch.setattr("pytask_r.execute.shutil.which", lambda x: None)

    session = main({"paths": tmp_path})

    assert session.exit_code == 1
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_rscript
@pytest.mark.end_to_end
def test_run_r_script_w_saving_workspace(tmp_path):
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

    assert session.exit_code == 0
    assert tmp_path.joinpath("out.txt").exists()
