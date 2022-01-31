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
    "pillow~=9.0.0",
    "matplotlib~=3.5.1",
]
extras_require = {
    "async": [
        "aioredis~=2.0.1",
    ],
}


# not really my code... (https://github.com/Rapptz/discord.py/blob/master/setup.py#L15)
if version[-1].isalpha():
    # append version identifier based on commit count
    try:
        import subprocess

        p = subprocess.Popen(
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()

        p = subprocess.Popen(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()

    except Exception as e:
        from warnings import warn

        warn(
            message=f"\033[31mUnable to append version identifier!\033[0m "
            f"\033[35m{e.__class__.__name__}: {e}\033[0m",
            category=UserWarning,
        )

setup(
    version=version,
    url=url,
    license=license,
    author=author,
    description=description,
    install_requires=install_requires,
    extras_require=extras_require,
)
