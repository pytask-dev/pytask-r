import shutil

import pytest


needs_rscript = pytest.mark.skipif(
    shutil.which("Rscript") is None, reason="R with Rscript needs to be installed."
)
