# standard library
import re
import sys
from pathlib import Path


# RegEx to find versions
VERSION_INIT_REGEX: re.Pattern[str] = re.compile(r"^(__version__\s*=\s*[\'\"])([^\'\"]*)([\'\"])", re.MULTILINE)
VERSION_TOML_REGEX: re.Pattern[str] = re.compile(r"^(version\s*=\s*[\'\"])([^\'\"]*)([\'\"])", re.MULTILINE)

# Paths to files to update
INIT_PATH: Path = Path(__file__).parent / "AlbertUnruhUtils/__init__.py"
TOML_PATH: Path = Path(__file__).parent / "pyproject.toml"


# Check whether files exist, fail if not
if not INIT_PATH.is_file():
    print(f"Invalid path for __init__.py: {INIT_PATH}", file=sys.stderr)
    sys.exit(1)

if not TOML_PATH.is_file():
    print(f"Invalid path for pyproject.toml: {INIT_PATH}", file=sys.stderr)
    sys.exit(1)

# Get file contents
init_text = INIT_PATH.read_text("utf-8", "ignore")
toml_text = TOML_PATH.read_text("utf-8", "ignore")

# Extract the current version
init_version_match = VERSION_INIT_REGEX.search(init_text)
toml_version_match = VERSION_TOML_REGEX.search(toml_text)

init_version = init_version_match.group(2) if init_version_match is not None else None
toml_version = toml_version_match.group(2) if toml_version_match is not None else None


# Check for consistency
if init_version != toml_version:
    print(
        f"Conflicting versions found in __init__.py and pyproject.toml: {init_version} | {toml_version}",
        file=sys.stderr,
    )
    sys.exit(1)


# Check whether a new version is provided
if len(sys.argv) != 2:  # noqa: PLR2004
    print("No new version provided as an argument!", file=sys.stderr)
    sys.exit(1)

new_version = sys.argv[1].removeprefix("v")


def _replacement_formatter(match: re.Match[str]) -> str:
    return f"{match.group(1)}{new_version}{match.group(3)}"


# Create replacement for previous match containing the new version
init_replacement = VERSION_INIT_REGEX.sub(_replacement_formatter, init_version_match.group(0))
toml_replacement = VERSION_TOML_REGEX.sub(_replacement_formatter, toml_version_match.group(0))

# Save updated versions
INIT_PATH.write_text(init_text.replace(init_version_match.group(0), init_replacement), "utf-8", "ignore")
TOML_PATH.write_text(toml_text.replace(toml_version_match.group(0), toml_replacement), "utf-8", "ignore")

print(f"Successfully updated version from {init_version} to {new_version}.")
sys.exit(0)
