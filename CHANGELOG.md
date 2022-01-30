# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased
/

## 2.0.x
### Added
- CHANGELOG.md was finally added
- README.md shows instructions how to install the `.asynchronous.*` part of the package

### Changed
- `.asynchronous.*` can't be imported with the from-statement (`from AlbertUnruhUtils import asynchronous` won't longer work)
- `.asynchronous.*` must be installed with the extra `async` (`pip install AlbertUnruhUtils.py[async]`)

### Fixed
- sorry PEP8, now you are more present (`__all__` is now at the top of the file and imports are alphabetically sorted)

## 1.0.x
### Added
- `.utils.logger` (for logging)
- `.utils.version` (to compare versions)
- `.ratelimit.server` (for server-site ratelimiting)
- `.config.jsonconfig` (for JSON-configuration files)
- `.asynchronous.ratelimit.server` (like `.ratelimit.server`, bur asynchronous)