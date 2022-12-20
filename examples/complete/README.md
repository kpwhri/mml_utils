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

If the number of files is really large, it can be useful to divide these into multiple separate filelists, each of which
can be run simultaneously (thereby parallel-processing the corpus). There are 2 ways to do this.

1. Specify the option `--n-dir 4` in the [`mml-csv-to-txt` command](#csv-to-txt) for 4 different directories of notes
   and 4 separate filelists
2. Run `mml-split-filelist filelist.txt 4` to split the `filelist.txt` into 4 separate parts (but keep all text in one
   directory).

Each of the filelists can be independently run against MetaMapLite and some efficiency will be gained (given number of
cores/memory constraints).

## Run with Metamaplite

Run Metamaplite using the filelist created before. Be sure to update full path to `--filelist` and the
appropriate `--mml-home`.

### mmi format

Command:

    mml-run-filelist --filelist C:/PATH/mml_utils/examples/complete/filelist.txt --mml-home C:/public_mm_lite --output-format mmi

Result:

* Adds a `.mmi` file MetaMapLite's output next to each `.txt` file.
* Creates a `filelist.txt_0` which is a copy of `filelist.txt`. Numbers after `0` implies that MetaMapLite ran with
  errors, and these were retried.

### json format

There may be certain limitations to json format including a lack of negation output (at time of writing:
PR: https://github.com/lhncbc/metamaplite/pull/16).

Command:

    mml-run-filelist --filelist C:/PATH/mml_utils/examples/complete/filelist.txt --mml-home C:/public_mm_lite --output-format json

Result:

* Adds a `.json` file MetaMapLite's output next to each `.txt` file.
* Creates a `filelist.txt_0` which is a copy of `filelist.txt`. Numbers after `0` implies that MetaMapLite ran with
  errors, and these were retried.

## Compile MML Output to CSV File

Compile mmi or json output to a CSV file. The `--outdir` must exist.

To limit to a certain number of cuis, create a file (e.g., `include-cuis.txt`) and place each CUI on a separate line.
See `include-cuis.txt` as an example.

Command:

    mml-extract-mml notes --outdir mmlout --cui-file include-cuis.txt --output-format mmi

Result:

* CSV file beginning with 'mml' containing an unpacked version of the mmi or json file
* CSV file beginning with 'notes' containing summary statistics on the notes in the corpus
* A log file with lots of errors for missing variables/column names.
    * To add these back into your output file, specify, e.g., `--add-fieldname negated fndg pos ...` and re-run.

## Generate Frequency Tables

Using the CSV files, we can generate frequency tables with these CUIs, or even grouping these CUIs as features.

A feature is a set of CUIs (1 or more) which are grouped together for analysis. Often, we are interested in `nausea`
regardless
of how many CUIs may have been identified (e.g., there are different CUIs for `nausea` and `feeling nauseous`, but we
want to include both in our counts).

Command:

    mml-build-freqs mml_csv_file.csv --feature-mapping feature_mapping.json --cui-definitions cui_definitions.csv
        --metadata-file metadata_file.csv --output-directory output_directory.csv --patient-count patient_count

### Arguments ###

* MML_CSV_FILE.csv
  * Output file from running `mml-extract-mml` (see [above](#compile-mml-output-to-csv-file))

* FEATURE_MAPPING.json
  * Mapping of `feature_name` -> `CUIs`. This will be a json file like:

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

* CUI_DEFINITIONS.json
  * CUI Definitions json file (optional; not all CUIs need to be included)

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

* METADATA_FILE.csv
  * File containing metadata for files that were processed by MML
  * Columns:
    * `studyid`: unique identifier per subject in the dataset; to ignore, set this to `docid`
    * `docid`: document identifer; should match `docid` in MML_CSV_FILE.csv
    * `date`: date of form `YYYY-MM-DD`; to ignore, assign unique dates to each `docid`

* OUTPUT_DIRECTORY
  * Path to output directory where output should be put; defaults to '.'
  * A subdirectory will be created within this output directory with a timestamp in which output files will be placed

* PATIENT_COUNT
  * Integer: number of patients/subjects
  * Why not just use METADATA_FILE.csv? This file is note-based rather than subject/patient-based. Certain individuals may lack notes
