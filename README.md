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
    <!-- a href="https://github.com/kpwhri/batch_metamaplite">
      <img src="images/logo.png" alt="Logo">
    </a -->
  </p>

  <h3 align="center">Utilities and Scripts for Running Metamaplite</h3>

  <p>
    Scripts for running Metamaplite against large batches of text.
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
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)



## About the Project 
The goal of this project is to put together various scripts to handle the preparation, running, and post-run extraction of results from Metamaplite.


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these steps.

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
    git clone https://github.com/kpwhri/batch_metamaplite.git
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

Take a directory with text documents (input files for metamaplite), organize them into groups of 100.000
    for subsequent processing. The subsequent processing will be done by related `mml-run-filelists-dir` command.

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

Metamaplite dumps the output `*.json` files in the same directory. If you want to rerun MML, either the `*.json` files or the notes need to be moved. This script will move the notes.

Assumptions:
* All notes have no extension.
  * To do this would require adding `Path.glob(*.txt)`, which might be a future change.


    mml-copy-notes --source /path/to/notes --dest /path/to/notes2


### mml-run-filelist

Run metamaplite against a single filelist. This has the advantage of automatically re-running if a file causes an error (and skipping it in the next run).

Each run will result in a newly-created filelist version.

    
    mml-run-filelist --filelist /path/to/filelist.txt --mml-home ./public_mm_lite


### mml-extract-mml

Extract results from running Metamaplite. Currently only supports json output.


    mml-extract-mml /path/to/notes [/path/to/notes2] --outdir /path/to/output --cui-file /only/include/these/cuis.txt

## Versions

Uses [SEMVER](https://semver.org/).

See https://github.com/kpwhri/batch_metamaplite/releases.

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/kpwhri/batch_metamaplite/issues) for a list of proposed features (and known issues).



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

Please use the [issue tracker](https://github.com/kpwhri/batch_metamaplite/issues). 


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/kpwhri/batch_metamaplite.svg?style=flat-square
[contributors-url]: https://github.com/kpwhri/batch_metamaplite/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/kpwhri/batch_metamaplite.svg?style=flat-square
[forks-url]: https://github.com/kpwhri/batch_metamaplite/network/members
[stars-shield]: https://img.shields.io/github/stars/kpwhri/batch_metamaplite.svg?style=flat-square
[stars-url]: https://github.com/kpwhri/batch_metamaplite/stargazers
[issues-shield]: https://img.shields.io/github/issues/kpwhri/batch_metamaplite.svg?style=flat-square
[issues-url]: https://github.com/kpwhri/batch_metamaplite/issues
[license-shield]: https://img.shields.io/github/license/kpwhri/batch_metamaplite.svg?style=flat-square
[license-url]: https://kpwhri.mit-license.org/
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/kaiserpermanentewashingtonresearch
<!-- [product-screenshot]: images/screenshot.png -->
