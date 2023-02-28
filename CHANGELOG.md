# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Reference

Types of changes:

* `Added`: for new features.
* `Changed`: for changes in existing functionality.
* `Deprecated`: for soon-to-be removed features.
* `Removed`: for now removed features.
* `Fixed`: for any bug fixes.
* `Security`: in case of vulnerabilities.


## [Unreleased]

### Added

- Stub for reporting AFEP results in an excel (and CSV) table(s).
- Added release checklist since was forgetting to update documentation version.

## [0.2.3]

### Added

- Updated AFEP process to include reading from cTAKES (requires specifying the `--data-directory` option)
- Including convenience methods to handle TUI and Semantic Type interactions

### Fixed

- Added default value when no semantic type in json output
- Avoiding pandas' SettingWithCopyWarning

## [0.2.2]

### Added

- Installation instructions for building UMLS subset for Metamaplite
- Documentation troubleshooting page
- Instructions on how to specify downloading a subset with MetamorphoSys

### Changed

- Metamaplite no longer runs the batch/shell script but creates the entire command line

## [0.2.1]

### Added

- Option to remove non-xml characters before cTAKES processes files
- Better logging information
- AFEP: Set minimum number of knowledge base articles in feature selection
- AFEP: Output details along with list of selected CUIs

## [0.2.0]

### Added

- Warnings to install pandas
- Script and documentation for building frequencies

## [0.1.3]

### Added

- Support for running and extracting data from cTAKES (including parsing xmi output files)
- Interactive version of MML to test running on text
- Ability to limit semantic types/sources

### Fixed

- Handle newline at end of mmi file
- Automatically create directories
- Improve mmi format parsing

## [0.1.2]

### Changed

- Converted parsing `triggerinfo` into a regular expression

### Fixed

- Made all tests pass in 3.8+

## [0.1.1]

### Changed

- Made code 3.8-compatible
- Limited logging in `mml-extract-mml`

## [0.1.0]

### Added

- Track previous samples to avoid re-sampling
- Examples for running `mml-extract-mml` in both json and mmi

### Changed

- Metadata CSV file will limit records selected from corpus in `mml-prepare-review` (`extract_data.py`)

### Fixed

- `Extract mml` with json format (crashing) fixed
- `Extract mml` with mmi format (crashing) fixed

## [0.0.9] - 2022-06-08

### Added

- End-to-end Examples
- Require at least version 8.0.0 of click

## [0.0.8] - 2022-06-06

### Added

- Script to automate creation of text files in a directory (i.e., building input for metamaplite)

## [0.0.7] - 2022-06-05

### Fixed

- Remove default sheet in Excel file
- Include final row in the formatted table (changed 0-index to 1-index)

## [0.0.6] - 2022-06-02

### Added

- Automatically build review files to Excel or CSV
