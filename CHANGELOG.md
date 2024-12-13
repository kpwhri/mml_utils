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

### Fixed

* cTAKES XMI output produces duplicate CUIs due to different codes; by default, only take the first now to more accurately represent CUI count

### Changed

* For extracting text to files, reduced memory footprint by only retaining most recent 10 records.

### Added

* Function/script to generate comparisons between different methods/approaches using Jaccard similarity
* Added support for generating text files from jsonlines using `mml-jsonl-to-txt`
* Resume an interrupted run of `mml-jsonl-to-text` (and other extract text files) by passing `--resume` argument
* Added script to remove already processed files from a filelist
* Added option to skip missing (i.e., unprocessed files) while running extraction
* Adding example from cTAKES


## [1.0.1] - 2024-10-16

### Fixed

* Error was raised when parsing cTAKES xmi files when the entity is not one of the target CUIs


## [1.0.0] - 2024-09-20

### Added

* Improved documentation, especially PheNorm example implementation of Anaphylaxis

### Fixed

* Ensured that `cuis_by_doc` output file contains all target CUIs from the CUI file



## [0.5.0] - 2024-08-16

### Added

* `--note-suffix` and `--output-suffix` if suffixes are different than those required (experimental)
* CUI normalization
* Documentation/docstrings including for PheNorm-specific use cases
* Improved logging with suggested troubleshooting methods
* Added support for SAS7BDAT files as an input corpus
* Extract MDR (MedDRA) LLTs (lower level terms) for a given set of PTs (primary terms)
* Always add newline when creating files for compatibility with MetaMap (tests fixed too)

### Fixed

* Skipping non-strings and empty notes when converting a corpus to files
* Click parameters not being accepted by function in `mml-extract-mml` function 



## [0.4.0] - 2023-12-19

### Added

* `pandas` as required rather than optional
* Generate pivot table when running `extract_mml` to show CUI counts note
* Documentation on using Metamap
* Timestamp to `cuis_by_doc` CSV output
* Added `cuis_by_doc.mmi.csv` as an example (this is referenced by the documentation)
* Tests for the complete examples in `./examples/complete` to ensure these work as expected

### Fixed

* Remove duplicate test
* `mml-extract-mml` was crashing on json input, so create default TargetCuis for json (already there in mmi)


## [0.3.6] - 2023-11-16

### Added

* Specify directory or file for `run_mml_filelist`
* Escapes for spaces and parens when building scripts
* Including a `start-servers` script as a reminder to kick-off required MM services
* Clean file ensures newline at end of each file (required by MM)

### Fixed

* Allow *.txt suffix when scanning for files


## [0.3.5] - 2023-09-28

### Added

- Enable multi-metamap builder to make replacements to the source posix path.
- All cui file to do transformations.
- Script to transform file from UTF-8 (or other encoding) to ASCII.

### Fixed

- Posix can't have quotes in the classpath when supplying argument to MM


## [0.3.4] - 2023-06-07

### Added

- Added logging
- Gave option to specify a max number of knowledge base articles (not just a min)
- Scripts to build metamap shell scripts by varying parameters, etc.
- Metamap shell script builder now generates a draft AFEP toml config
- more AFEP configs can be grouped in MultiAfepConfig to reduce amount of redundant configurations
- Updated README with new metamap script builder commands
- Can specify file or directory when running mml, and a filelist will automatically be created

### Fixed

- Fixed bug when running AFEP with a single set of data.
- Force Excel summary tab name length to be <= 31.


## [0.3.3] - 2023-05-25

### Changed

- Remove default UMLS version/dataset from `run_mml` and allow these as specified by parameters
  - If nothing specified, default to looking up available datasets, defaulting to `USAbase` dataset


## [0.3.2] - 2023-05-24

### Added

- Using `charset_normalizer` package to read files correctly (with file encoding) before splitting. This should probably be used more broadly...eventually.


## [0.3.1] - 2023-05-23

### Added

- Check for MMI in second field earlier in the process (to avoid parsing failures)
- Run Metamaplite on a single file rather than requiring a filelist


## [0.3.0] - 2023-04-24 (Added Metamap Support)

### Added

- Reporting AFEP results in an excel (and CSV) table(s).
- Added release checklist since was forgetting to update documentation version.
- Diffs tab to Excel AFEP summary
- Multi-version AFEP runner using a TOML config file
- Console scripts to `pyproject.toml` for new functionality
- Test for building AFEP summary table
- Added documentation for AFEP commands
- Run comparisons between summary files (i.e., files generated by `mml-extract-mml`)
- Tests to support metamap's mmi file (this seems to include extra brackets, but still parsed correctly)
- Doco for installing/using metamap
- Add `all_semantictypes` and `all_sources` to mmi output
- Skip metamap acronym/abbreviation lines
- Change `min_kb` to allow setting globally in `run_afep_multi`

### Fixed

- Random requires `list`, not `set`
- Updated `pyproject.toml` for new flit version
- Migrated `pytest_lazy_fixture` to new format (i.e., no longer able to call from pytest directly) 
- Changed mmi parser to handle commas/semicolons more appropriately

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

### Fixed

- Remove default sheet in Excel file
- Include final row in the formatted table (changed 0-index to 1-index)

## [0.0.6] - 2022-06-02

### Added

- Automatically build review files to Excel or CSV


[unreleased]: https://github.com/kpwhri/mml_utils/compare/1.0.1...HEAD
[1.0.1]: https://github.com/kpwhri/mml_utils/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/kpwhri/mml_utils/compare/0.5.0...1.0.0
[0.5.0]: https://github.com/kpwhri/mml_utils/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/kpwhri/mml_utils/compare/0.3.6...0.4.0
[0.3.6]: https://github.com/kpwhri/mml_utils/compare/0.3.5...0.3.6
[0.3.5]: https://github.com/kpwhri/mml_utils/compare/0.3.4...0.3.5
[0.3.4]: https://github.com/kpwhri/mml_utils/compare/0.3.3...0.3.4
[0.3.3]: https://github.com/kpwhri/mml_utils/compare/0.3.2...0.3.3
[0.3.2]: https://github.com/kpwhri/mml_utils/compare/0.3.1...0.3.2
[0.3.1]: https://github.com/kpwhri/mml_utils/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/kpwhri/mml_utils/compare/0.2.3...0.3.0
[0.2.3]: https://github.com/kpwhri/mml_utils/compare/0.2.2...0.2.3
[0.2.2]: https://github.com/kpwhri/mml_utils/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/kpwhri/mml_utils/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/kpwhri/mml_utils/compare/0.1.3...0.2.0
[0.1.3]: https://github.com/kpwhri/mml_utils/compare/0.1.2...0.1.3
[0.1.2]: https://github.com/kpwhri/mml_utils/compare/0.1.1...0.1.2
[0.1.1]: https://github.com/kpwhri/mml_utils/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/kpwhri/mml_utils/compare/0.0.9...0.1.0
[0.0.9]: https://github.com/kpwhri/mml_utils/compare/0.0.8...0.0.9
[0.0.8]: https://github.com/kpwhri/mml_utils/compare/0.0.6...0.0.8
[0.0.6]: https://github.com/kpwhri/mml_utils/releases/0.0.6
