from pathlib import Path

from setuptools import find_packages
from setuptools import setup

import versioneer


README = Path("README.rst").read_text()

PROJECT_URLS = {
    "Documentation": "https://github.com/pytask-dev/pytask-latex",
    "Github": "https://github.com/pytask-dev/pytask-latex",
    "Tracker": "https://github.com/pytask-dev/pytask-latex/issues",
    "Changelog": "https://github.com/pytask-dev/pytask-latex/blob/main/CHANGES.rst",
}


setup(
    name="pytask-r",
    version=versioneer.get_version(),
    cmd_class=versioneer.get_cmdclass(),
    description="Run R scripts with pytask.",
    long_description=README,
    long_description_content_type="text/x-rst",
    author="Tobias Raabe",
    author_email="raabe@posteo.de",
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: R",
    ],
    platforms="any",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={"pytask": ["pytask_r = pytask_r.plugin"]},
    zip_false=False,
)
