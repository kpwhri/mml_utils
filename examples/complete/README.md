
# Instructions/Commands for Using MML Utils

## Prerequisites

* Install Python
* Install MetaMapLite
  * See instructions here: https://kpwhri.github.io/mml_utils/install_metamaplite.html
  * You will need to remember install location (e.g., `C:/public_mm_lite`)
* Install `mml_utils` with `pip install .`
* Navigate to `examples/complete` directory: `cd examples/complete`
* If you want to follow along, copy the `corpus.csv` to a different directory and `cd` there.

## CSV to Text

There is a CSV file in `corpus.csv` which needs to be converted to a directory containing files which MML can read.

Command:

    mml-csv-to-txt corpus.csv --id-col note_id --text-col text

Result:

* This will create a folder called `notes` containing 6 files with a `.txt` extension.
* A file called `filelist.txt` with a list of all the files in the `notes` directory.

## [ASIDE] Split into Multiple Filelists

If the number of files is really large, it can be useful to divide these into multiple separate filelists, each of which can be run simultaneously (thereby parallel-processing the corpus). There are 2 ways to do this.

1. Specify the option `--n-dir 4` in the [`mml-csv-to-txt` command](#csv-to-txt) for 4 different directories of notes and 4 separate filelists
2. Run `mml-split-filelist filelist.txt 4` to split the `filelist.txt` into 4 separate parts (but keep all text in one directory).

Each of the filelists can be independently run against MetaMapLite and some efficiency will be gained (given number of cores/memory constraints).


## Run with Metamaplite

Run Metamaplite using the filelist created before. Be sure to update full path to `--filelist` and the appropriate `--mml-home`.

### mmi format

Command:

    mml-run-filelist --filelist C:/PATH/mml_utils/examples/complete/filelist.txt --mml-home C:/public_mm_lite --output-format mmi

Result:

* Adds a `.mmi` file MetaMapLite's output next to each `.txt` file.
* Creates a `filelist.txt_0` which is a copy of `filelist.txt`. Numbers after `0` implies that MetaMapLite ran with errors, and these were retried.

### json format

There may be certain limitations to json format including a lack of negation output (at time of writing: PR: https://github.com/lhncbc/metamaplite/pull/16). 

Command:

    mml-run-filelist --filelist C:/PATH/mml_utils/examples/complete/filelist.txt --mml-home C:/public_mm_lite --output-format json

Result:

* Adds a `.json` file MetaMapLite's output next to each `.txt` file.
* Creates a `filelist.txt_0` which is a copy of `filelist.txt`. Numbers after `0` implies that MetaMapLite ran with errors, and these were retried.

