from setuptools import find_packages
from setuptools import setup

setup(
    name="pytask-r",
    version="0.0.6",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"pytask": ["pytask_r = pytask_r.plugin"]},
)
