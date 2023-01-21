from __future__ import annotations

import shutil

import pytest
from click.testing import CliRunner


needs_rscript = pytest.mark.skipif(
    shutil.which("Rscript") is None, reason="R with Rscript needs to be installed."
)


parametrize_parse_code_serializer_suffix = pytest.mark.parametrize(
    "parse_config_code, serializer, suffix",
    [
        (
            "library(jsonlite); args <- commandArgs(trailingOnly=TRUE); "
            "config <- read_json(args[length(args)])",
            "json",
            ".json",
        ),
        (
            "library(yaml); args <- commandArgs(trailingOnly=TRUE); "
            "config <- read_yaml(args[length(args)])",
            "yaml",
            ".yaml",
        ),
    ],
)


@pytest.fixture()
def runner():
    return CliRunner()
