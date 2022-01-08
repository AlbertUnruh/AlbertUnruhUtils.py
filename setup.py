from setuptools import setup
import re


with open("./AlbertUnruhUtils/__init__.py") as f:
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


# not in setup.cfg for GitHub's Dependency-Graph
install_requires = [
    "redis~=4.1.0",
    "aioredis~=2.0.1",
]


setup(
    version=version,
    url=url,
    license=license,
    author=author,
    description=description,
    install_requires=install_requires,
)
