.. image:: https://img.shields.io/pypi/v/pytask-r?color=blue
    :alt: PyPI
    :target: https://pypi.org/project/pytask-r

.. image:: https://img.shields.io/pypi/pyversions/pytask-r
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/pytask-r

.. image:: https://img.shields.io/conda/vn/conda-forge/pytask-r.svg
    :target: https://anaconda.org/conda-forge/pytask-r

.. image:: https://img.shields.io/conda/pn/conda-forge/pytask-r.svg
    :target: https://anaconda.org/conda-forge/pytask-r

.. image:: https://img.shields.io/pypi/l/pytask-r
    :alt: PyPI - License
    :target: https://pypi.org/project/pytask-r

.. image:: https://img.shields.io/github/workflow/status/pytask-dev/pytask-r/Continuous%20Integration%20Workflow/main
   :target: https://github.com/pytask-dev/pytask-r/actions?query=branch%3Amain

.. image:: https://codecov.io/gh/pytask-dev/pytask-r/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/pytask-dev/pytask-r

.. image:: https://results.pre-commit.ci/badge/github/pytask-dev/pytask-r/main.svg
    :target: https://results.pre-commit.ci/latest/github/pytask-dev/pytask-r/main
    :alt: pre-commit.ci status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

------

pytask-r
========

Run R scripts with pytask.


Installation
------------

pytask-r is available on `PyPI <https://pypi.org/project/pytask-r>`_ and `Anaconda.org
<https://anaconda.org/conda-forge/pytask-r>`_. Install it with

.. code-block:: console

    $ pip install pytask-r

    # or

    $ conda install -c conda-forge pytask-r

You also need to have R installed and ``Rscript`` on your command line. Test it by
typing the following on the command line

.. code-block:: console

    $ Rscript --help

If an error is shown instead of a help page, you can install R with ``conda`` by
choosing either R or Microsoft R Open (MRO). Choose one of the two following commands.
(See `here <https://docs.anaconda.com/anaconda/user-guide/tasks/ using-r-language>`_
for further explanation on Anaconda, R, and MRO.)

.. code-block:: console

    $ conda install -c r r-base     # For normal R.
    $ conda install -c r mro-base   # For MRO.

Or install install R from the official `R Project <https://www.r-project.org/>`_.


Usage
-----

Similarly to normal task functions which execute Python code, you define tasks to
execute scripts written in R with Python functions. The difference is that the function
body does not contain any logic, but the decorator tells pytask how to handle the task.

Here is an example where you want to run ``script.r``.

.. code-block:: python

    import pytask


    @pytask.mark.r
    @pytask.mark.depends_on("script.r")
    @pytask.mark.produces("out.rds")
    def task_run_r_script():
        pass

Note that, you need to apply the ``@pytask.mark.r`` marker so that pytask-r handles the
task.

If you are wondering why the function body is empty, know that pytask-r replaces the
body with a predefined internal function. See the section on implementation details for
more information.


Multiple dependencies and products
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What happens if a task has more dependencies? Using a list, the R script which should be
executed must be found in the first position of the list.

.. code-block:: python

    @pytask.mark.r
    @pytask.mark.depends_on(["script.r", "input.rds"])
    @pytask.mark.produces("out.rds")
    def task_run_r_script():
        pass

If you use a dictionary to pass dependencies to the task, pytask-r will, first, look
for a ``"source"`` key in the dictionary and, secondly, under the key ``0``.

.. code-block:: python

    @pytask.mark.r
    @pytask.mark.depends_on({"source": "script.r", "input": "input.rds"})
    def task_run_r_script():
        pass


    # or


    @pytask.mark.r
    @pytask.mark.depends_on({0: "script.r", "input": "input.rds"})
    def task_run_r_script():
        pass


    # or two decorators for the function, if you do not assign a name to the input.


    @pytask.mark.r
    @pytask.mark.depends_on({"source": "script.r"})
    @pytask.mark.depends_on("input.rds")
    def task_run_r_script():
        pass


Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

The decorator can be used to pass command line arguments to ``Rscript``. See the
following example.

.. code-block:: python

    @pytask.mark.r("value")
    @pytask.mark.depends_on("script.r")
    @pytask.mark.produces("out.rds")
    def task_run_r_script():
        pass

And in your ``script.r``, you can intercept the value with

.. code-block:: r

    args <- commandArgs(trailingOnly=TRUE)
    arg <- args[1]  # holds ``"value"``


Parametrization
~~~~~~~~~~~~~~~

You can also parametrize the execution of scripts, meaning executing multiple R scripts
as well as passing different command line arguments to the same R script.

The following task executes two R scripts which produce different outputs.

.. code-block:: python

    from src.config import BLD, SRC


    @pytask.mark.r
    @pytask.mark.parametrize(
        "depends_on, produces",
        [(SRC / "script_1.r", BLD / "1.rds"), (SRC / "script_2.r", BLD / "2.rds")],
    )
    def task_execute_r_script():
        pass

And the R script includes something like

.. code-block:: r

    args <- commandArgs(trailingOnly=TRUE)
    produces <- args[1]  # holds the path

If you want to pass different command line arguments to the same R script, you have to
include the ``@pytask.mark.r`` decorator in the parametrization just like with
``@pytask.mark.depends_on`` and ``@pytask.mark.produces``.

.. code-block:: python

    @pytask.mark.depends_on("script.r")
    @pytask.mark.parametrize(
        "produces, r",
        [(BLD / "output_1.rds", "1"), (BLD / "output_2.rds", "2")],
    )
    def task_execute_r_script():
        pass


Configuration
-------------

If you want to change the name of the key which identifies the R script, change the
following default configuration in your pytask configuration file.

.. code-block:: ini

    r_source_key = source


Implementation Details
----------------------

The plugin is a convenient wrapper around

.. code-block:: python

    import subprocess

    subprocess.run(["Rscript", "script.r"], check=True)

to which you can always resort to when the plugin does not deliver functionality you
need.

It is not possible to enter a post-mortem debugger when an error happens in the R script
or enter the debugger when starting the script. If there exists a solution for that,
hints as well as contributions are highly appreciated.


Changes
-------

Consult the `release notes <CHANGES.rst>`_ to find out about what is new.
