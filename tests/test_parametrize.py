import os
import textwrap

import pytest
from conftest import needs_rscript
from pytask.main import main


@needs_rscript
@pytest.mark.end_to_end
def test_parametrize_r_options(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.depends_on("script.r")
    @pytask.mark.parametrize("produces, r", [("0.rds", "0"), ("1.rds", "1")])
    def task_execute_r_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    latex_source = r"""
    args <- commandArgs(trailingOnly=TRUE)
    number <- args[1]
    saveRDS(number, file=paste0(number, ".rds"))
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(latex_source))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("0.rds").exists()
    assert tmp_path.joinpath("1.rds").exists()
