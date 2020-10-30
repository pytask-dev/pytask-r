"""Contains test which ensure that the plugin works with pytask-parallel."""
import os
import textwrap
import time

import pytest
from conftest import needs_rscript
from pytask import cli

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
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_files(runner, tmp_path):
    """Test parallelization over source files.

    Same as in README.rst.

    """
    os.chdir(tmp_path)

    source = """
    import pytask

    @pytask.mark.r
    @pytask.mark.parametrize(
        "depends_on, produces", [("script_1.r", "1.rds"), ("script_2.r", "2.rds")]
    )
    def task_execute_r_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    r_script = """
    Sys.sleep(1.5)
    saveRDS(1, file=paste0(1, ".rds"))
    """
    tmp_path.joinpath("script_1.r").write_text(textwrap.dedent(r_script))

    r_script = """
    Sys.sleep(1.5)
    saveRDS(2, file=paste0(2, ".rds"))
    """
    tmp_path.joinpath("script_2.r").write_text(textwrap.dedent(r_script))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0
    duration_normal = time.time() - start

    for name in ["1.rds", "2.rds"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == 0
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal


@needs_rscript
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_file(runner, tmp_path):
    """Test parallelization over the same source file.

    Same as in README.rst.

    """
    os.chdir(tmp_path)

    source = """
    import pytask

    @pytask.mark.depends_on("script.r")
    @pytask.mark.parametrize(
        "produces, r",
        [
            ("output_1.rds", (["--vanilla", "1"],)),
            ("output_2.rds", (["--vanilla", "2"],)),
        ],
    )
    def task_execute_r_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    r_script = """
    Sys.sleep(1.5)
    args <- commandArgs(trailingOnly=TRUE)
    number <- args[2]
    saveRDS(number, file=paste0("output_", number, ".rds"))
    """
    tmp_path.joinpath("script.r").write_text(textwrap.dedent(r_script))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0
    duration_normal = time.time() - start

    for name in ["output_1.rds", "output_2.rds"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == 0
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal
