import shutil

import pytest
from click.testing import CliRunner

needs_rscript = pytest.mark.skipif(
    shutil.which("Rscript") is None, reason="R with Rscript needs to be installed."
)


@pytest.fixture()
def runner():
    return CliRunner()
