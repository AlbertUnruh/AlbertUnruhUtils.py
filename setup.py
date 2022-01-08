from setuptools import setup
from pathlib import Path
import re


__path__ = Path(__file__).parent.absolute()


with open(__path__ / "AlbertUnruhUtils/__init__.py") as f:
    file = f.read()

version = re.search(
    r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", file, re.MULTILINE
).group(1)
url = re.search(r"^__url__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", file, re.MULTILINE).group(1)
license = re.search(  # noqa
    r"^__license__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", file, re.MULTILINE
).group(1)
author = re.search(
    r"^__author__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", file, re.MULTILINE
).group(1)
description = re.search(
    r"^__description__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", file, re.MULTILINE
).group(1)


with open(__path__ / "./README.md") as f:
    long_description = f.read()

with open(__path__ / "./requirements.txt") as f:
    requirements = f.readlines()


name = "AlbertUnruhUtils"
packages = [
    f"{name}",
    f"{name}.config",
    f"{name}.ratelimit",
    f"{name}.asynchronous",
    f"{name}.asynchronous.ratelimit",
]


setup(
    name=name,
    version=version,
    packages=packages,
    url=url,
    license=license,
    author=author,
    description=description,
    long_description=long_description,
    install_requires=requirements,
)
