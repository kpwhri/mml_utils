[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div>
  <p>
    <!-- a href="https://github.com/kpwhri/mml_utils">
      <img src="images/logo.png" alt="Logo">
    </a -->
  </p>

<h3 align="center">Utilities and Scripts for Running Metamaplite</h3>

  <p>
    Scripts for running Metamaplite (MML) against large batches of text.
  </p>
</div>


<!-- TABLE OF CONTENTS -->

## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
* [Usage](#usage)
    * [Run Metamaplite in Batches](#run-metamaplite-in-batches)
    * [Copy Notes to Re-run: mml-copy-notes](#mml-copy-notes)
    * [Run MML Against a Filelist: mml-run-filelist](#mml-run-filelist)
    * [Extract MML Results: mml-extract-mml](#mml-extract-mml)
    * [Check MML Progress: mml-extract-mml](#mml-check-progress)
    * [Split MML Filelist: mml-split-filelist](#mml-split-filelist)
    * [Split Long File: mml-split-files](#mml-split-files)
    * [Run AFEP on MML Output: mml-run-afep](#mml-run-afep)
    * [Check How Closely Offsets Match: mml-check-offsets](#mml-check-offsets)
    * [Prepare CSV Files for Review: mml-prepare-review](#mml-prepare-review)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)

## About the Project

The goal of this project is to put together various scripts to handle the preparation, running, and post-run extraction
of results from Metamaplite.


<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these steps.

Additional instructions, including UMLS/MML installation are described here: https://kpwhri.github.io/mml_utils/.

### Prerequisites

* Python 3.9+
* pip install .
    * See pyproject.toml for updated dependencies.

### Installation

0. Setup a virtual environment
    ```shell
    python -m venv .venv 
    ```
1. Clone the repo
    ```sh
    git clone https://github.com/kpwhri/mml_utils.git
    ```
2. Install the package (using pyproject.toml)
    ```sh
    pip install .
    ```

## Usage

### Run Metamaplite in Batches

These scripts assume the following use case:

* Files are currently being written/built to the target directory.
* You want to start running Metamaplite on those records that have already been written
* The total number of files can be unknown.

These scripts will repeatedly look for new files, build filelists, and run Metamaplite.

#### mml-build-filelists

Prepare files for running metamaplite.

Take a directory with text documents (input files for metamaplite), organize them into groups of 100.000 for subsequent
processing. The subsequent processing will be done by related `mml-run-filelists-dir` command.

Arguments:

    * --outpath OUTPATH
        - This is more of a workspace. Input documents are expected under `outpath`/clarity.
        - Target files (text documents) will be moved from `clarity` to `mml`
        - Files with groups of 100.000 text documents will be plaaced in `mml_lists` subdirectory.

Example:

    mml-build-filelists --outpath /path/to/dir
        - /path/to/dir
            - clarity [assumes exists with text documents]
                - 001.txt
                - 002.txt
                - etc.
            - mml [starts empty; text documents will be moved here]
                - 001.txt
                - 002.txt
                - etc.
            - mml_lists [starts empty; lists of files in `mml` directory will be placed here
                - files_[date].in_progress  [100.000 references to `mml` directory; ready for processing]
                - files_[date].in_progress  [100.000 references to `mml` directory; ready for processing]
                - files_[date].building  [currently being built; don't process]

After, run `mml-run-filelists-dir` to process all these files. Their extension will be changed to `.complete`.

#### mml-run-filelists-dir

Run metamaplite from `mml_lists` and `mml` directory created by `build_filelists.py`.

Arguments:

    * --mml-home PATH
        - Path to install directory of Metamaplite. This will be placed as path to executable.

    * --filedir PATH
        - Path to mml_lists directory (output from `build_filelists.py`).
        - Must choose one of the numbered outputs.
        - Will only process current `in_progress` (reads at initialization; doesn't keep checking for new files)

Example:

    mml-run-filelists-dir --mml-home ./public_mm_lite --filedir /path/to/dir/mml_lists/0

### mml-copy-notes

Copy files from a completed MML directory to a new one to re-run MML.

Metamaplite dumps the output `*.json` files in the same directory. If you want to rerun MML, either the `*.json` files
or the notes need to be moved. This script will move the notes.

Assumptions:

* All notes have no extension.
    * To do this would require adding `Path.glob(*.txt)`, which might be a future change.

  mml-copy-notes --source /path/to/notes --dest /path/to/notes2

### mml-run-filelist

Run metamaplite against a single filelist. This has the advantage of automatically re-running if a file causes an
error (and skipping it in the next run).

Each run will result in a newly-created filelist version. Default output format is `json`.

    mml-run-filelist --filelist /path/to/filelist.txt --mml-home ./public_mm_lite [--output-format (mmi|json)]

### mml-extract-mml

Extract results from running Metamaplite. Currently supports json (default) or MMI output.

    mml-extract-mml /path/to/notes [/path/to/notes2] --outdir /path/to/output --cui-file /only/include/these/cuis.txt [--output-format (mmi|json)]

### mml-check-progress

Check progress of Metamaplite running in a single directory.

    mml-check-progress /path/to/notes

To enable repeatedly checking, e.g., every 24 hours (and outputting results to log):

    mml-check-progress /path/to/notes --repeat-hours 24

To have the process stop before a certain date or after a certain number of hours, use either of these:

    mml-check-progress /path/to/notes --repeat-end-after-hours 168   # 1 week
    mml-check-progress /path/to/notes --repeat-end-after-datetime 2030-01-01   # will not run after this time

### mml-split-filelist

Split a filelist into multiple parts (to allow for parallelizing MML).

This command will generate 3 separate files (`filelist.txt_part0`, `filelist.txt_part1`, and `filelist.txt_part2`), each
containing 1/3. (`partN` will contain lines where `line_number % 3 == N`.)

    mml-split-filelist filelist.txt 3

Each of these output files can be fed separately into [`mml-run-filelist`](#mml-run-filelist)

### mml-split-files

Some files are too long for MML to properly parse (at least in a reasonable amount of time). This script will split the
long file into ones of (by default) 200 lines, adding all the resulting files to a new `filelist.txt`.

    mml-split-files Medscape.txt Wikipedia.txt [--n-lines 200] [--filelist filelist.txt] 

This will produce files like this:

* Medscape_0.txt
* Medscape_1.txt
* Medscape_n.txt
* Wikipedia_0.txt
* Wikipedia_1.txt
* Wikipedia_n.txt
* filelist.txt  <- Run this file using [`mml-run-filelist`](#mml-run-filelist).

### mml-run-afep

This is not directly related to MML. If, however, you want to implement AFEP, this and
the [previous section](#mml-split-files) may be of some use.

1. Download text from Knowledge Base sources (e.g., Medline, Medscape, Merck, Wikipedia, Mayo) on your target
   condition (e.g., arthritis or COVID-19).
2. Name these text files something like 'Medscape.txt' and 'Wikipedia.txt' and place them in a new directory (
   e.g., `/kb_articles/`).
3. Split the files into no more than say 200 lines (see [mml-split-files](#mml-split-files) command for assistance).
4. Run MML on the entire directory (e.g., `/kb_articles/`).
5. Run [mml-run-afep](#mml-run-afep) on the output (see parametrisation below).

As a prerequisite, you'll need to install pandas (`pip install pandas`) which is not installed by default due to this
being the only script requiring it.

    mml-run-afep /kb_articles/ [--mml-format json|mmi] [--outdir .]

### mml-check-offsets

Confirm that the offsets reported by MML are correct.


    mml-check-offsets /path/to/notes

If running MML on Windows, include `--add-cr` to add back carriage returns.

Use `--replacements old==new` to make certain changes to 'fix' the matches.


### mml-prepare-review

Prepare review lists of CSV files.

Inputs (see `tests/fever` for examples:
* Text file (`feature.cui.txt`) containing target CUIs, 1 per line
* String file (`feature.string.txt`) containing text strings to look for and include with CUI data


    mml-prepare-review /path/to/notes --target-path /path/to/inputs [--mml-format json] [--text-extension .txt] [--text-encoding utf8]




## Versions

Uses [SEMVER](https://semver.org/).

See https://github.com/kpwhri/mml_utils/releases.

<!-- ROADMAP -->

## Roadmap

See the [open issues](https://github.com/kpwhri/mml_utils/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->

## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the MIT License.

See `LICENSE` or https://kpwhri.mit-license.org for more information.



<!-- CONTACT -->

## Contact

Please use the [issue tracker](https://github.com/kpwhri/mml_utils/issues).


<!-- ACKNOWLEDGEMENTS -->

## Acknowledgements

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/kpwhri/mml_utils.svg?style=flat-square

[contributors-url]: https://github.com/kpwhri/mml_utils/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/kpwhri/mml_utils.svg?style=flat-square

[forks-url]: https://github.com/kpwhri/mml_utils/network/members

[stars-shield]: https://img.shields.io/github/stars/kpwhri/mml_utils.svg?style=flat-square

[stars-url]: https://github.com/kpwhri/mml_utils/stargazers

[issues-shield]: https://img.shields.io/github/issues/kpwhri/mml_utils.svg?style=flat-square

[issues-url]: https://github.com/kpwhri/mml_utils/issues

[license-shield]: https://img.shields.io/github/license/kpwhri/mml_utils.svg?style=flat-square

[license-url]: https://kpwhri.mit-license.org/

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555

[linkedin-url]: https://www.linkedin.com/company/kaiserpermanentewashingtonresearch
<!-- [product-screenshot]: images/screenshot.png -->
