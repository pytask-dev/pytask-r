from setuptools import find_packages
from setuptools import setup

import versioneer


setup(
    name="pytask-r",
    version=versioneer.get_version(),
    cmd_class=versioneer.get_cmdclass(),
    description="Run R scripts with pytask.",
    packages=find_packages(where="src"),
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
    ],
    platforms="any",
    package_dir={"": "src"},
    entry_points={"pytask": ["pytask_r = pytask_r.plugin"]},
    zip_false=True,
)
