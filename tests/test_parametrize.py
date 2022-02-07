from __future__ import annotations

import os
import textwrap

import pytest
from conftest import needs_rscript
from pytask import main


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
def test_parametrize_r_options_and_product_paths(tmp_path):
    task_source = """
    import pytask
    from pathlib import Path

    SRC = Path(__file__).parent

    @pytask.mark.depends_on("script.r")
    @pytask.mark.parametrize("produces, r", [
        (SRC / "0.rds", (0, SRC / "0.rds")), (SRC / "1.rds", (1, SRC / "1.rds"))
    ])
    def task_execute_r_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    r_script = """
    args <- commandArgs(trailingOnly=TRUE)
    number <- args[1]
    produces <- args[2]
    saveRDS(number, file=produces)
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("0.rds").exists()
    assert tmp_path.joinpath("1.rds").exists()
