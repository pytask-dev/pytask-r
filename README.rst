.. image:: https://anaconda.org/pytask/pytask-r/badges/version.svg
    :target: https://anaconda.org/pytask/pytask-r

.. image:: https://anaconda.org/pytask/pytask-r/badges/platforms.svg
    :target: https://anaconda.org/pytask/pytask-r

.. image:: https://github.com/pytask-dev/pytask-r/workflows/Continuous%20Integration%20Workflow/badge.svg?branch=main
    :target: https://github.com/pytask-dev/pytask-r/actions?query=branch%3Amain

.. image:: https://codecov.io/gh/pytask-dev/pytask-r/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/pytask-dev/pytask-r

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

------

pytask-r
========

pytask-r allows you to run R scripts with pytask.


Installation
------------

Install the plugin with

.. code-block:: console

    $ conda config --add channels conda-forge --add channels pytask
    $ conda install pytask-r

You also need to have R installed and ``Rscript`` on your command line. To test
whether it is installed, type the following on the command line

.. code-block:: console

    $ Rscript --help

If an error is shown instead of a help page, you can install R with ``conda`` by
choosing either the normal R or Microsoft R Open (MRO). The command is one of the two
following commands. (See `here <https://docs.anaconda.com/anaconda/user-guide/tasks/
using-r-language>`_  for further explanation on Anaconda, R, and MRO.)

.. code-block:: console

    $ conda install -c r r-base     # For normal R.
    $ conda install -c r mro-base   # For MRO.

Or install install R from the official `R Project <https://www.r-project.org/>`_.


Usage
-----

Similarly to normal task functions which execute Python code, you also define tasks to
execute scripts written in R with Python functions. The difference is that the function
body does not contain any logic, but the decorators tell pytask how to handle the task.

Here is an example where you want to run ``script.r``.

.. code-block:: python

    import pytask


    @pytask.mark.r
    @pytask.mark.depends_on("script.r")
    @pytask.mark.produces("out.rds")
    def task_run_r_script():
        pass

Note that, you need to apply the ``@pytask.mark.r`` marker so that pytask-r handles the
task. The executable script must be the first dependency. Other dependencies can be
added after that.

.. code-block:: python

    @pytask.mark.r
    @pytask.mark.depends_on(["script.r", "input.rds"])
    @pytask.mark.produces("out.rds")
    def task_run_r_script():
        pass

If you are wondering why the function body is empty, know that pytask-r replaces the
body with an predefined internal function. See the section on implementation details for
more information.


Command Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

The decorator can be used to pass command line arguments to ``Rscript`` which is, by
default, only the ``--vanilla`` flag. If you want to pass arguments to the script via
the command line, use

.. code-block:: python

    @pytask.mark.r(["--vanilla", "value"])
    @pytask.mark.depends_on("script.r")
    @pytask.mark.produces("out.rds")
    def task_run_r_script():
        pass

And in your ``script.r``, you can intercept the value with

.. code-block:: r

    args <- commandArgs(trailingOnly=TRUE)
    arg <- args[1]  # ``arg`` holds ``"value"``


Parametrization
~~~~~~~~~~~~~~~

You can also parametrize the execution of scripts, meaning executing multiple R scripts
as well as passing different command line arguments to an R script.

The following task executes two R scripts which produce different outputs.

.. code-block:: python

    @pytask.mark.r
    @pytask.mark.parametrize(
        "depends_on, produces", [("script_1.r", "1.rds"), ("script_2.r", "2.rds")]
    )
    def task_execute_r_script():
        pass


If you want to pass different command line arguments to the same R script, you have to
include the R decorator in the parametrization just like with
``@pytask.mark.depends_on`` and ``@pytask.mark.produces``.

.. code-block:: python

    @pytask.mark.depends_on("script.r")
    @pytask.mark.parametrize("produces, r", [("out_1.rds", 1), ("out_2.rds", 2)])
    def task_execute_r_script():
        pass


.. _implementation_details:

Implementation Details
----------------------

The plugin is only a convenient wrapper around

.. code-block:: python

    import subprocess

    subprocess.run(["Rscript", "--vanilla", "script.r"], check=True)

to which you can always resort to when the plugin does not deliver functionality you
need.

It is not possible to enter a post-mortem debugger when an error happens in the R script
or enter the debugger when starting the script. If there exists a solution for that,
hints as well as contributions are highly appreciated.


Changes
-------

Consult the `release notes <CHANGES.rst>`_ to find out about what is new.
