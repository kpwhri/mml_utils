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
    Tools for running Metamaplite, Metamap, and cTAKES and interpreting their output.
  </p>
</div>


<!-- TABLE OF CONTENTS -->

## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
* [Usage](#usage)
    * [End to End Example](examples/complete/README.md)
    * Commands
        * [Build MetaMapLite Directory from SQL/CSV](#mml-to-txt)
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
        * [Build Frequncy Tables](examples/complete/README.md#generate-frequency-tables)
        * [Build Metamap Sheel Script](#build-metamap-scripts-mml-build-mmscript--mml-build-mmscript-multi)
        * [Compare Multiple Output Files]()
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

* Recommended Python 3.11+
    * Okay: Python 3.9+
    * Some portions of the code may require 3.11
* `pip install .`
    * See `pyproject.toml` for updated dependencies.

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

## Data Formats

| Tool        | Encoding | Requires Newline | Allows Spaces in Path | Must Run in Text Directory |
|-------------|----------|------------------|-----------------------|----------------------------|
| Metamap     | ?        | : Y            : | : N:                  | :N:                        |
| Metamaplite | ?        | : N            : | : N:                  | :Y:                        |
| cTAKES      | ?        | : N            : | : Y:                  | :Y:                        |

## Usage

### End-to-End Example

There are several examples in the `examples` directory.

* [Complete Example](examples/complete/README.md)
* [Phenorm-focused Example](examples/phenorm/README.md)
* [cTAKES Example](examples/ctakes/README.md)


In the `examples/complete/` directory, you can find a complete end-to-end example of build and running MetaMapLite. One
using `*.json` and the other `*.mmi` formats.

Please see [README.md](examples/complete/README.md) file there for step-by-step instructions.

This examples will lead you through:

* Installing metamaplite (MML)
* Installing this package
* Running MML on a sample CSV dataset
* Extracting results
* Generating frequency tables

### Data Preparation

#### Corpus

Apart from just installing the code, you'll need to prepare and format your data. This can often be quite
time-consuming as you'll need to select a cohort, time windows, etc.
Prepare this data to look like the [corpus.csv file](examples/complete/corpus.csv) with columns of:

* `studyid`
* `docid`
* `text`

Also, create a `metadata_file.csv` which contains:

* `studyid`
* `docid`
* `date`: as `YYYY-MM-DD`
* ...other fields which may be of interest.

For MetaMapLite (MML) to read the data, you'll need all the text in a single directory.
The name of each note should be `DOCID.txt` (Python: `f'{docid}.txt'`).
See the [end-to-end examples](examples/complete/README.md) for commands to convert
[CSV to Text](examples/complete/README.md#csv-to-text) and
[creating filelists](examples/complete/README.md#aside-split-into-multiple-filelists).

#### Supplementary Files

In addition to the corpus files, several JSON files can be useful for summarizing data (building frequencies, etc.).

##### CUI Definitions

A CUI Definitions json file can be constructed defining the different CUIs that are be targeted.
This is particularly useful when building frequency files
([`mml-build-freqs` command](examples/complete/README.md#generate-frequency-tables)).

By compiling a list of CUIs in a txt file, this file can be built automatically with a script from the
[
`umls_api_tool` package](https://github.com/dcronkite/umls_api_tool/blob/master/examples/cui/cui_to_best_definition.py).

Here's an example:

```json
[
  {
    "cui": "C0027497",
    "definition": "Nausea"
  },
  {
    "cui": "C0027498",
    "definition": "Nausea and vomiting"
  }
]
```

##### Feature Mapping

In certain applications, multiple CUIs will be grouped into a single *feature* or *category*.
A JSON file should be generated grouping these together. CUIs may appear in multiple features.

Mapping of `feature_name` -> `CUIs`. This will be a json file like:

```json
[
  {
    "feature": "Nausea",
    "cuis": [
      "C0027498",
      "C0027497"
    ]
  },
  {
    "feature": "Vomiting",
    "cuis": [
      "C0027498",
      "C0221151",
      "C1510416",
      "C0152165",
      "C0020450",
      "C0042963"
    ]
  },
  {
    "feature": "Diarrhea",
    "cuis": [
      "C0011991"
    ]
  }
]
```

### Run Metamaplite in Batches

These scripts assume the following use case:

* Files are currently being written/built to the target directory.
* You want to start running Metamaplite on those records that have already been written
* The total number of files can be unknown.

These scripts will repeatedly look for new files, build filelists, and run Metamaplite.

#### mml-to-txt

Prepare files for running metamaplite. Files can be in CSV file or SQL database.

Additional Options (for both sql/csv):

* `--n-dirs [INTEGER]`
    * Number of directories to create with text files. Defaults to 1
* `--text-encoding utf8`
    * If you want the files in an encoding other than `utf8`, please specify. Be sure to test what MetaMapLite is able
      to handle.
* `--text-extension ".txt"`
    * Another option is to have no extension for these files. In that case, specify an empty string.

##### mml-sql-to-txt

For SQL, you will need to install `sqlalchemy` and a driver (e.g., `pyodbc` for SQL Server as in the example below).

* `pip install sqlalchemy pyodbc`

The first two arguments are the SqlAlchemy-style connection string, followed by the query to retrieve (note_id, text).

Example:

    mml-sql-to-txt "mssql+pyodbc://SERVER/DATABASE?driver=SQL+Server" "select note_id, note_text from corpus" --outdir OUTDIR

##### mml-csv-to-txt

For CSV, you will need to specify the id and text columns.

Example:

    mml-csv-to-txt /path/to/corpus.csv --outdir OUTDIR --id-col note_id --text-col note_text

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

If the processing gets interrupted, a new filelist can be built using the `mml-clean-filelist` command. The location of the filelist will be retained (a backup of the original will be placed in the same location with a `.bk` suffix).

    mml-clean-filelist /path/to/filelist.txt [--output-format (mmi|json)] [--output-directory /path/to/outdir]

* `--output-format` defaults to looking for `json`
* `--output-directory` defaults to assuming input and output are in same directory (as done for MetaMapLite)
* Once this is done, re-run `mml-run-filelist --filelist /path/to/filelist.txt ...`
  * The original filelist will be renamed with a tiemstamp.

### mml-extract-mml

Extract results from running Metamaplite, Metamap, or cTAKES. Currently supports json (default), xmi (ctakes), and mmi. This command assumes
that the mmi/json files from Metamaplite are on the same path as the text files/notes. If this is not the case, specify
the path to the text files/notes in `/path/to/notes` and use `--output-directory` to specify where the output files are.

*Important assumptions about extensions:* ideally the extensions to all text files will be `.txt` (or no extension) and
those to the output formats for for Metamaplite/cTAKES are `.mmi`, `.json`, or `.txt.xmi`. If this is not the case, you
can try the experimental `--output-suffix` and `--notes-suffix` (if not `.txt`). In addition, the *stem* of both the
note and the relevant output file must be identical. If possible, use only a single `.` (period, dot) in the filename (
i.e., prefer not using multiple suffixes).

    mml-extract-mml /path/to/notes [/path/to/notes2] --outdir /path/to/output --cui-file /only/include/these/cuis.txt [--extract-format (mmi|json|xmi)]

For usage with cTAKES output, include the `--extract-directory [CTAKES_XMI_DIR]` which points to the cTAKES output
directory.

    mml-extract-mml /path/to/notes --outdir /path/to/output [...] --extract-directory /path/to/*.xmi.txt_dir --extract-format xmi

For encoding challenges, you can use the following arguments:

* `--file-encoding`: encoding that the text notes are written/saved in (e.g., 'latin1', 'utf8')
* `--output-encoding`: encoding that the program (i.e., Metamaplite or cTAKES) wrote the output to

*Alternative: Extract to Text*

Importantly, the above `mml-extract-mml` will use the perspective of the notes when identifying extractions. If your notes are only partially processed (e.g., you're trying to get intermediary results), it may make sense to just iterate across all of the processed NLP extracts rather than notes. For this, we would use `mml-extract`. In pseudocode, here's the difference between the approaches:

```python

# mml-extract-mml

for note in notes:
    nlp_extract = get_nlp_results(note)
    write_output(note, nlp_extract)

# mml-extract
for extract in extracts:
    note = get_note(extract)
    write_output(extract, note)

```

    mml-extract /path/to/extract [/path/to/extract2] --outdir /path/to/output --cui-file /only/include/these/cuis.txt [--output-format (mmi|json|xmi)] [--note-directory /path/to/notes] [--note-directory /path/to/notes2]

* The `--note-directory` argument is only required if it differs from the extract directory (i.e., required for cTAKES).
* If `/path/to/extract` is the output of `/path/to/notes`, and `/path/to/extract2` is the output of the notes in `/path/to/notes2`, esnure that they are listed in the same order. This will speed up the processing. 

#### mml-compare-extracts

To compare two different feature extraction processes (e.g., cTAKES + MedDRA vs MML + MedDRA), place the
relevant `notes` and `mml` csv files into directories named after the feature extraction. This command is
directory-based rather than file-based, so both outputs cannot be in the same folder. For the following example (
generated from `mml-extract-mml`...

    ct_meddra / notes_20230329.csv
    ct_meddra / mml_20230329.csv
    mml_meddra / notes_20230329.csv
    mml_meddra / mml_20230329.csv

...use this command:

    mml-compare-extracts ct_meddra mml_meddra

This will create a comparison CSV file called 'compare_ct_meddra_mml_meddra.csv' in the current directory showing the
differences.

More generally, the command:

    mml-compare-extracts EXTRACT_DIR_1 EXTRACT_DIR_2 [--outpath OUTPUT_DIR] [--text-encoding (utf|latin1|etc.)] [--name1 NAME] [--name2 NAME2]

The `--name#` arguments are to override the default names which are based on the directories.

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

Or, you can specify an entire directory with files as below:

    mml-split-files kb-articles [--n-lines 200]

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

An Excel table showing the resulting CUIs can then be built by running:

    mml-summarize-afep OUTDIR(outdirectory from `mml-run-afep` command)

If experimenting with multiple approaches (e.g., cTAKES+MedDRA vs MML+MedDRA vs ...), you can run these all in a single
command:

    mml-run-afep-multi config.toml

Example TOML (an example can be generated using `write_afep_script_for_dirs`):

    outdir = 'path/output_dir'
    
    [[runs]]
    note_directories = ['/path/to/usabase']
    
    [[runs]]
    note_directories = ['/path/to/meddra']
    name = 'mdr'  # use 'mdr' as output name rather than 'meddra'
    
    [[runs]]
    note_directories = ['/path/to/kb_articles']
    data_directory = ['/path/to/ctakes_meddra']
    expand_cuis = True
    apikey = '1234-5678-9101'

This will run AFEP three times and then create an Excel file containing the summary measures.

### Build Metamap Scripts: mml-build-mmscript / mml-build-mmscript-multi

Build a metamap shell script can be a bit of a challenge since the metamap executable expects specifying only a single
target file and a single output file. Instead of building this manually, `mml-build-mmscript` (for single
configurations) and `mml-build-mmscript-multi` (for comparing multiple metamap configurations).

An example config using the `mml-build-mmscript-multi`:

    outpath = 'C:/metamap/scripts'
    filelist = 'C:/metamap/kb_filelist.txt'
    mm_outpath = '/mnt/c/output'
    parameters = '-R MDR,RXNORM -Z 2022AB -V NLM -N'  # shared parameters, will be prefixed
    
    [[runs]]
    # the first run with unique metamap parameters
    parameters = '-y -C --conj'
    name = 'relaxed_wsd_conj'
    
    [[runs]]
    # another configuration
    parameters = '-y -C'
    name = 'relaxed_wsd'
    
    [[runs]]
    parameters = '-C --conj'
    name = 'conj'

### mml-check-offsets

Confirm that the offsets reported by MML are correct.

    mml-check-offsets /path/to/notes

If running MML on Windows, include `--add-cr` to add back carriage returns.

Use `--replacements old==new` to make certain changes to 'fix' the matches (e.g., special characters).

### mml-prepare-review

Prepare review lists of CSV files.

Inputs (see `tests/fever` for examples:

* Text file (`feature.cui.txt`) containing target CUIs, 1 per line
* String file (`feature.string.txt`) containing text strings to look for and include with CUI data

  mml-prepare-review /path/to/notes --target-path
  /path/to/inputs [--mml-format json] [--text-extension .txt] [--text-encoding utf8]

To then take samples from this dataset, use `mml-prepare-review-sample`.

### Compare Multiple Offset Files with `mml-compare`

Compare outputs of different configurations, vocabularies, or tools with `mml_compare`.

To run this, specify an output directory and the directories containing `cuis_by_doc_*.csv` files. The `*` stands for
the date. By default, the most recent version will be included.

An example config follows. We specify each `cui_by_doc` file we want compared. This includes:
* `ct`: run using cTAKES
* `mm`: run using MetaMap
* `mml`: run using MetaMapLite
* `joined`: if note had multiple lines, we joined them
* `lined`: lined version of note, where docid was given name `{docid}_{linenum}` (e.g., 12487_1)
The goal of this analysis was to compare performance of NLP extraction tools when the raw notes were not joined together and see if htis had a degrading performance (it did not have an appreciable difference).


    --outdir
    /path/to/compare
    --compare
    joined-ct_fast==/path/to/joined/ct_fast/out
    --compare
    joined-ct_rx_mdr==/path/to/joined/ct_rx_mdr/out
    --compare
    joined-mm_default==/path/to/joined/mm_default/out
    --compare
    joined-mm_rx_mdr==/path/to/joined/mm_rx_mdr/out
    --compare
    joined-mml_default==/path/to/joined/mml_default/out
    --compare
    lined-ct_fast==/path/to/lined/ct_fast/out
    --compare
    lined-ct_rx_mdr==/path/to/lined/ct_rx_mdr/out
    --compare
    lined-mm_default==/path/to/lined/mm_default/out
    --compare
    lined-mm_rx_mdr==/path/to/lined/mm_rx_mdr/out
    --compare
    lined-mml_default==/path/to/lined/mml_default/out


## Troubleshooting

* If there is a problem with file encoding (e.g., an error like 'unable to decode byte'), the above programs should
  provide some method for specifying the encoding:
    * Example options: `--text-encoding` / `--file-encoding`, `--output-encoding`
    * Example encodings to try for English: `utf8`, `latin1`

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
