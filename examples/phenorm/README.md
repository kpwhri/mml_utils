# Instructions/Command for Using MML Utils for PheNorm

This guide will provide instructions on using the `mml_utils` package to implement the PheNorm algorithm as defined in the [Sentinel Scalable NLP Github repo](https://github.com/kpwhri/Sentinel-Scalable-NLP). We will focus on Anaphylaxis for which the `cuis.txt` is setup.

## Prerequisites

* Install Python
* Install MetaMapLite 
    * See instructions here: https://kpwhri.github.io/mml_utils/install_metamaplite.html
    * You will need to remember install location (e.g., `C:/public_mm_lite`)
* Install `mml_utils` by:
  * Cloning this repository `git clone https://github.com/kpwhri/mml_utils`
  * Installing with `cd mml_utils` and `pip install .` 
* SAS7BDAT files output from the SAS pipeline
  * You can find an example dataset in `examples/phenorm` (navigate here to follow along)
  * If using multiple datasets, run them each separately (or ensure that the `note-id` field does not overlap).


## Dataset to Text

Beginning with `corpus.sas7bdat` (or, alternatively, `corpus.csv`), convert these to files where they can be processed by tools like MetaMap, MetaMapLite, etc.

Command:

    mml-sas-to-txt corpus.sas7bdat --id-col note_id --text-col note_text [--n-dir 4] [--outdir OUTDIR]

* `--n-dir INTEGER`: create `INTEGER` number of folders/filelists; this will allow for easy parallelization when using MetaMapLite (but added complications when using MetaMap)
* For CSV files, use `mml-csv-to-txt`.
* For a database table, use `mml-sql-to-txt`.
* `--outdir PATH`: location to place 'output' (see below); defaults to current directory

Output:
* A folder `notes` (or multiple folders `notesN`) containing text files with note text.
* A file `filelist.txt` (or multiple) with the path to each text file for processing with MetaMapLite or MetaMap.


## Run Extraction Using an NLP Tool

UMLS CUIs must be extracted using an NLP tool. Either MetaMapLite (easiest) or MetaMap are recommended, and helper scripts are included in this module (see below). A module for cTAKES is also available.

A version of the UMLS is also required. While MetaMapLite comes with a pre-built subset, it does not include the recommended MDR (i.e., Meddra) subset. Please follow the steps here: https://kpwhri.github.io/mml_utils/build_umls_for_mml.html#building-custom-subset

### MetaMapLite

#### Prerequisites

* Install MetaMapLite: https://kpwhri.github.io/mml_utils/install_metamaplite.html
* MDR UMLS Subset: https://kpwhri.github.io/mml_utils/build_umls_for_mml.html#building-custom-subset

#### Running MetaMapLite

The easiest way to run MetaMapLite is to instruct it to process a single filelist. Parallelization can be achieved by running against multiple filelists. For each filelist, use the following command:

Command:

    mml-run-filelist --filelist filelist.txt --mml-home C:/public_mm_lite --output-format json

* Recommended output format is `json` (although `mmi` is also supported)
* `--mml-home` is the full path to the folder where MetaMapLite was installed.

Output:
* Alongside each `{note_id}.txt` file will be a corresponding `{note_id}.json` file with generated output (e.g., the identified CUIs).

### MetaMap

#### Prerequisites

* Install MetaMap: https://kpwhri.github.io/mml_utils/install_mm.html
* MDR UMLS Subset: https://kpwhri.github.io/mml_utils/build_umls_for_mml.html#building-custom-subset

#### Running MetaMap

It is worth acquainting yourself with some brief MetaMap documentation [here](https://kpwhri.github.io/mml_utils/install_mm.html#run-metamap), before continuing. 

You may wish to run MetaMap without the aid of the `mml_utils` package. (The `mml_utils` packages was designed to run a number of experiments with varying configurations, not for a single run for which it might prove a bit clunky.) If you choose not to use it, run all your files and continue to the next heading. Windows users, in particular, may find benefit in the `mml_utils` package (see below).

First, you'll need to start the part of speech and word sense disambiguation servers (these are found in the `public_mm` directory from installing MetaMap:
* `./bin/skrmedpostctl start`
* `./bin/wsdserverctl start`

Second, instead of directly calling MetaMap, `mml_utils` will attempt to generate configuration files to run MetaMap. These should be looked over before running. We'll create a `.toml` file called `config.toml` with the following contents (full paths are preferred to avoid errors). An example `toml` file is provided below

```toml
# Create shell scripts to run metamap on corpus
# Usage:
# 1. Build the shell scripts: `mml-build-mmscript-multi run_mm_on_corpus.toml`
# 2. Run the shell scripts in the `outpath`
# 3. Build the output
outpath = 'C:\workspace\scripts'  # path to write Metamap-running shell scripts to
filelist = 'C:\workspace\corpus\filelist.txt'  # newline-separated list of files
mm_outpath = '/mnt/c/workspace/mmout'  # output location for Metamap mmi/json files
mm_path = '/mnt/c/public_mm/bin/metamap'  # full path to metamap executable (otherwise, defaults to assuming public_mm/bin is on PATH)
parameters = '-R MDR,RXNORM -Z 2022AB -V NLM -N'  # parameters to run Metamap with
num_scripts = 3  # number of scripts to prepare (i.e., enabling parallel processing of notes)
replace = ['C:', '/mnt/c']

# here is the run we used, though other configuration options can be provided in a separate run
[[runs]]
parameters = '-y'
name = 'wsd'
```

* `outpath`: where the scripts will be placed
* `filelist`: filelist where filepaths should be collected from
* `mm_outpath`: output folder for MetaMap output files
* `parameters`: any command line parameters to supply MetaMap
* `num_scripts`: more scripts will allow for parallelization
* `replace`: any replacements; this will be useful on Windows when running this under WSL
* `[[runs]]`: you can use multiple of these headings to allow running with different configurations
* `parameters`: any parameters to add just for this particular `run`
* `name`: give this configuration a recognizable name

Command:

    mml-build-mmscript-multi config.toml

This will create a `scripts` directory (or whatever you supplied to `outpath`) of 2 files along with one for each of the `num_scripts`. NB: On Windows, these must be run on WSL.

* `start_servers.sh`: commands to start the WSD and POS servers; show a relative path (you will need to navigate to the MetaMap home directory `cd public_mm`)
* `ensure_directories`: make sure output directories exist
* `script_N.sh`: these contain commands to run MetaMap; since MetaMap cannot run on a folder/filelist, each file must be run individually
  * it may be worth testing out the first command, fixing it if it doesn't run properly, and then doing a global find/replace to make sure all the commands will work

## Extracting CUIs

Once the appropriate NLP tool has been run, we will build a CSV file to include only the CUIs we are interested in (e.g., related to Anaphylaxis).

Command:

    mml-extract-mml notes --outdir mmlout --cui-file cuis.txt --output-format mmi|json
  

* `--output-format`: pick either `mmi` or `json` depending on whether the NLP tool output mmi or json files
* `--outdir`: output will be placed here
* `--cui-file`: file containing the target CUIs to include, along with any mappings (where appropriate)
* `notes`: directory containing raw files and NLP tool CUI annotations

Output:

* CSV file beginning with 'mml' containing an unpacked version of the mmi or json file
* CSV file beginning with 'notes' containing summary statistics on the notes in the corpus
* A log file with lots of errors for missing variables/column names.
    * To add these back into your output file, specify, e.g., `--add-fieldname negated fndg pos ...` and re-run.

  

## Next Steps

These NLP outputs must be merged with structured data (in SAS) and then passed on for modeling in R.

Some possible post-processing steps include:
* selecting a subset of CUIs grouped by patient/event
* looking at negated mentions
* improving dataset formatting

### Select Subset of CUIs

It may prove useful to select a subset of CUIs and group by a 'patient' or 'event' (e.g., as silver standard labels). To do this, we might do something like:

```python

import pandas as pd


df = pd.read_csv('mml_20240814_160954.csv')  # Output from `Extracting CUIs` step
target_cuis = [  # a list of our target CUIs
    'C4316895',
    'C0685898',
    'C0340865',
    'C0002792',
    'C0854649',
]
shared_cuis = set(df['cui'].unique()) & set(target_cuis)  # what CUIs are actually in the data?
# select only those rows with the target cuis
res_df = df[df['cui'].isin(target_cuis)].groupby(
    ['docid', 'cui']
)['start'].count().unstack().fillna(0).reset_index().applymap(int)
# res_df has columns `cui`, `docid`, and `C#######`
xwalk_df = pd.read_csv(...)  # a crosswalk from `docid` to `studyid`/`event_id`

res_df = pd.merge(xwalk_df, res_df, how='left', left_on='note_id', right_on='docid').fillna(0).applymap(int)
res_df.to_csv(f'selected_cuis_{len(shared_cuis)}.csv', index=False)

```

### Negated Mentions

```python

import pandas as pd


df = pd.read_csv('mml_20240814_160954.csv')  # Output from `Extracting CUIs` step
df = df[['docid', 'cui', 'negated']]
df = df.rename(columns={'docid': 'note_id'})
cuis = list(df['cui'].unique())
res = df[df['cui'].isin(cuis)].groupby('cui').agg({
    'note_id': 'count',
    'negated': 'sum',
})
res['non_negated'] = res['note_id'] - res['negated']

# output: dataset with `cui`, `note_id`, `negated`, and `non_negated` 
```

### Positive and Negated Datasets


```python

import pandas as pd


df = pd.read_csv('mml_20240814_160954.csv')  # Output from `Extracting CUIs` step
df = df[['docid', 'cui', 'negated']]
df = df.rename(columns={'docid': 'note_id'})
neg_df = df.copy()
neg_df['cui'] = df.apply(lambda x: f"{x['cui']}_neg" if x['negated'] else x['cui'], axis=1)
del df['negated']
del neg_df['negated']
df['count'] = 1
neg_df['count'] = 1
df = df.pivot_table(index='note_id', columns='cui', values='count', fill_value=0, aggfunc=sum).reset_index()
neg_df = neg_df.pivot_table(index='note_id', columns='cui', values='count', fill_value=0, aggfunc=sum).reset_index()

xwalk_df = pd.read_csv(...)  # contains, e.g., `note_id`, and `event_id`/`studyid`

df = pd.merge(xwalk_df, df, how='left', on='note_id').fillna(0).applymap(int)
neg_df = pd.merge(xwalk_df, neg_df, how='left', on='note_id').fillna(0).applymap(int)

# output results
df.to_csv('data.csv', index=False)  # does not distinguish negated/non-negated results
neg_df.to_csv('data_neg.csv', index=False)  # negated results recorded under `C#######_neg` fields
# Output: `event_id`, `note_id`, `C#######`, and (in `data_neg.csv`) `C#######_neg`
```


