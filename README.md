# pytask-r

[![PyPI](https://img.shields.io/pypi/v/pytask-r?color=blue)](https://pypi.org/project/pytask-r)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytask-r)](https://pypi.org/project/pytask-r)
[![image](https://img.shields.io/conda/vn/conda-forge/pytask-r.svg)](https://anaconda.org/conda-forge/pytask-r)
[![image](https://img.shields.io/conda/pn/conda-forge/pytask-r.svg)](https://anaconda.org/conda-forge/pytask-r)
[![PyPI - License](https://img.shields.io/pypi/l/pytask-r)](https://pypi.org/project/pytask-r)
[![image](https://img.shields.io/github/actions/workflow/status/pytask-dev/pytask-r/main.yml?branch=main)](https://github.com/pytask-dev/pytask-r/actions?query=branch%3Amain)
[![image](https://codecov.io/gh/pytask-dev/pytask-r/branch/main/graph/badge.svg)](https://codecov.io/gh/pytask-dev/pytask-r)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pytask-dev/pytask-r/main.svg)](https://results.pre-commit.ci/latest/github/pytask-dev/pytask-r/main)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

______________________________________________________________________

Run R scripts with pytask.

## Installation

pytask-r is available on [PyPI](https://pypi.org/project/pytask-r) and
[Anaconda.org](https://anaconda.org/conda-forge/pytask-r). Install it with

```console
$ pip install pytask-r

# or

$ conda install -c conda-forge pytask-r
```

You also need to have R installed and `Rscript` on your command line. Test it by typing
the following on the command line

```console
Rscript --help
```

If an error is shown instead of a help page, you can install R with `conda`.

```console
conda install -c conda-forge r-base
```

Or install install R from the official [R Project](https://www.r-project.org/).

## Usage

To create a task that runs an R script, define a task function with the `@mark.r`
decorator. The `script` keyword provides an absolute path or a path relative to the task
module.

```python
from pathlib import Path
from pytask import mark


@mark.r(script=Path("script.r"))
def task_run_r_script(produces: Path = Path("out.rds")):
    pass
```

If you are wondering why the function body is empty, know that pytask-r replaces the
body with a predefined internal function. See the section on implementation details for
more information.

### Dependencies and Products

Dependencies and products can be added as usual. See this
[tutorial](https://pytask-dev.readthedocs.io/en/stable/tutorials/defining_dependencies_products.html)
for some help.

### Accessing dependencies and products in the script

To access the paths of dependencies and products in the script, pytask-r stores the
information by default in a `.json` file. The path to this file is passed as a
positional argument to the script. Inside the script, you can read the information.

```r
library(jsonlite)

args <- commandArgs(trailingOnly=TRUE)

path_to_json <- args[length(args)]

config <- read_json(path_to_json)

config$produces  # Is the path to the output file "../out.csv".
```

The `.json` file is stored in the same folder as the task in a `.pytask` directory.

To parse the JSON file, you need to install
[jsonlite](https://github.com/jeroen/jsonlite).

You can also pass any other information to your script by using the `@task` decorator.

```python
from pathlib import Path
from pytask import mark, task


@task(kwargs={"number": 1})
@mark.r(script=Path("script.r"))
def task_run_r_script(produces: Path = Path("out.rds")):
    pass
```

and inside the script use

```r
config$number  # Is 1.
```

### Debugging

In case a task throws an error, you might want to execute the script independently from
pytask. After a failed execution, you see the command that executed the R script in the
report of the task. It looks roughly like this

```console
Rscript <options> script.r <path-to>/.pytask/task_py_task_example.json
```

### Command Line Arguments

The decorator can be used to pass command line arguments to `Rscript`. See the following
example.

```python
@mark.r(script=Path("script.r"), options="--vanilla")
def task_run_r_script(produces: Path = Path("out.rds")):
    pass
```

### Repeating tasks with different scripts or inputs

You can also repeat the execution of tasks, meaning executing multiple R scripts or
passing different command line arguments to the same R script.

The following task executes two R scripts, `script_1.r` and `script_2.r`, which produce
different outputs.

```python
for i in range(2):

    @task
    @mark.r(script=Path(f"script_{i}.r"))
    def task_execute_r_script(produces: Path = Path(f"out_{i}.csv")):
        pass
```

If you want to pass different inputs to the same R script, pass these arguments with the
`kwargs` keyword of the `@task` decorator.

```python
for i in range(2):

    @task(kwargs={"i": i})
    @mark.r(script=Path("script.r"))
    def task_execute_r_script(produces: Path = Path(f"output_{i}.csv")):
        pass
```

and inside the task access the argument `i` with

```r
library(jsonlite)

args <- commandArgs(trailingOnly=TRUE)

path_to_json <- args[length(args)]

config <- read_json(path_to_json)

config$produces  # Is the path to the output file "../output_{i}.csv".

config$i  # Is the number.
```

### Serializers

You can also serialize your data with any other tool you like. By default, pytask-r also
supports YAML (if PyYaml is installed).

Use the `serializer` keyword arguments of the `@pytask.mark.r` decorator with

```python
@mark.r(script=Path("script.r"), serializer="yaml")
def task_example(): ...
```

And, in your R script use

```r
library(yaml)
args <- commandArgs(trailingOnly=TRUE)
config <- read_yaml(args[length(args)])
```

Note that the `YAML` package needs to be installed.

If you need a custom serializer, you can also provide any callable `serializer` which
transforms data into a string. Use `suffix` to set the correct file ending.

Here is a replication of the JSON example.

```python
import json


@mark.r(script=Path("script.r"), serializer=json.dumps, suffix=".json")
def task_example(): ...
```

### Configuration

You can influence the default behavior of pytask-r with configuration values.

**`r_serializer`**

Use this option to change the default serializer.

```toml
[tool.pytask.ini_options]
r_serializer = "json"
```

**`r_suffix`**

Use this option to set the default suffix of the file which contains serialized paths to
dependencies and products and more.

```toml
[tool.pytask.ini_options]
r_suffix = ".json"
```

**`r_options`**

Use this option to set default options for each task which are separated by whitespace.

```toml
[tool.pytask.ini_options]
r_options = ["--vanilla"]
```

## Changes

Consult the [release notes](CHANGES.md) to find out about what is new.
