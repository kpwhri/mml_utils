
# Extracting Concepts Using MetaMap

Use case: I want to use MetaMap to extract concepts from the UMLS. This document will cover building configuration files to run `metamap`.

Since the focus of this documentation is on usage of the `mml_utils` package, it will be assumed that this is installed (but it is definitely not required). Note that in the case of Metamap, `mml_utils` **cannot** be the sole intermediary. Instead, it will generate shell scripts which must be run in a Linux (or WSL) environment.

## Setup/Prerequisites

* Installation is discussed [elsewhere](install_mm.md#install-metamap)
  * The install directory will be referred to as `$MM_HOME`
* Installation of UMLS for MM is discussed [elsewhere](install_mm.md#download-datasets)
* Text files
  * These *must* end in a newline, otherwise the final line will not be processed.
* Filelist
  * Create a text file with the full path to each of the text files to be processed on a separate line. E.g., `C:\path\to\1.txt\nC:\path\to\2.txt\n[...]`

> **Warning**  
> **Text files must have a newline at the end**: This is a bit sparse in the Metamap documentation, but if a line does not end in a newline character (\n), that line will not be processed. Practically, this only applies to the last line. 
> To fix, you can always open the file and press `ENTER` at the end of the last line.
> In Python, something like `outfile.write(infile.read() + '\n')` is sufficient.

## Build Config Files and Shell Scripts

To generate the shell scripts, create a configuration file in the TOML format called `config.toml`. This shell script can handle creating multiple sub-configurations if you want to run Metamap with different sets of parameters. Each of these sub-configurations is called a 'run'.

> **Warning**
> **Forbidden Characters in the File Paths**: Metamap's file parser will throw errors for certain file paths (e.g., a path with parenthesis like: `C:\projects\grant1 (asthma)\corpus\file1.txt`). I'm not going to list all of the problematic tokens, but prefer using alphanumerics without spaces (use capitalization \[CamelCase\] or underscores \[snake_case\] to separate tokens).

In providing an example configuration, I'm going to use Windows-based examples since these are more challenging to encode correctly (i.e., certain elements need to be Windows-formatted paths and others need to be Unix-styled paths). For other OSs, just use all *normal* (i.e., Unix-style) paths. For Windows, follow the examples below carefully.

### Format/definition

For all `run`s, these are the global definitions.

```toml
outpath = 'PATH for output scripts'
filelist = 'PATH to corpus filelist'
mm_outpath = 'PATH for metamap to write files, use Unix-style path'
parameters = 'CONFIGURATION parameters for all runs'
num_scripts = 'Number of scripts to run (this allows parallelization'
replace = 'List of any replacements in the path to apply; useful for Windows -> Unix conversions.'
mm_path = '$MM_PATH'
```

For each `run`, a `[[runs]]` must be provided. All parameters supplied here with either *add* or *overwrite* the higher level components. E.g., `parameters` will *add* to the global set, whereas `outpath` with *overwrite*.

```toml
[[runs]]
parameters = '(Required) Any parameters specific for this run, adds to the global set'
name = '(Required) Arbitrary (though hopefully useful) name'
mm_outpath = '(Optional) overwrite `mm_outpath` from global level' 
```

### Example `config.toml`
The following `config.toml` will run the 2022AB UMLS corpus on the NLM subset using MDR (Meddra) and RXNORM.

```toml
outpath = 'C:/project/extract/metamap/scripts'
filelist = 'C:\project\corpora\corpus1\filelist_corpus1.txt'
mm_outpath = '/mnt/c/project/extract/metamap/mmout'
parameters = '-Z 2022AB -V NLM -R MDR,RXNORM -N'
num_scripts = 4
replace = ['C:', '/mnt/c']
mm_path = '/mnt/c/public_mm'

[[runs]]
parameters = ''
name = 'rxnorm_mdr'

[[runs]]
parameters = '-y'
name = 'rxnorm_mdr_y'

[[runs]]
parameters = '--negex'
name = 'rxnorm_mdr_negation'
```

### Run `config.toml` to Build Scripts

Once the `config.toml` is ready, building the scripts is as simple as running:

* `mml-build-mmscript-multi config.toml`

Please note that `mml_utils` must be installed to make this work (run `cd mml_utils; pip install .`)

This will create (when using the [Example Config above](#example-configtoml)) an output file `scripts` with at least three different shell scripts which will be explained below.

In addition to these three scripts, a `run_afep_{date}.toml` config file will also be generated. This file will need editing, but can be passed to `mml-run-afep-multi` to run AFEP (Automated Feature Engineering for Phenotyping) on the extracted output. See [below](#run-afep).

## Running Metamap

Here we will use the scripts generated by the `config.toml` run in the previous step. This will consist of three scripts (or, *types* of scripts) which should be run in the order below:

* `ensure_directories.sh`
  * Ensure that required output directories exist
* `start_servers.sh`
  * Start the WSD and POS taggers
  * May need to prefix these with `$MM_PATH` if `mm_path` was not included
* `script_N.sh`
  * Scripts that will actually run Metamap
  * These are divided into separate processes

With all scripts, it is worth at least taking a quick look at the files to make sure that reasonable defaults have been included.

Also, if you need to mount a particular drive (e.g., WSL on Windows), use `mount -t drvfs C: /mnt/c`.

### Ensure Directories

This script makes sure the correct output directories actually exist.

### Start Servers

This script will start the WSD and POS tagging servers. This only needs to be completed once on each server/computer this is being run on. Each of the `script_N.sh` shell scripts will need to communicate with these servers.

### Run Metamap

These will run Metamap.

* If you just see `metamap`, ensure `$MMPATH/bin` is on the path
  * `PATH=$PATH:/mnt/c/public_mm/bin`

The format of this file will look like:
* `metamap` or `$MM_PATH`
* The parameters
* The input file (`*.txt`)
* The output file (`*.mmi`)

Run each script in a separate shell script (and ensure that `$MM_PATH/bin` is on the `$PATH` in each shell).


## Extracting CUIs from Metamap Output

Once all of the `script_N.sh` shell scripts have finished running (and it's a good idea to glance at the last few to make sure there aren't any devious errors), you'll want to get the CUIs out of the output.

To accomplish this, we'll run `mml-extract-mml` which will read all of the `*.mmi` files and extract all (or a specified subset of) CUIs. This will generate three output files.

* `mml.csv`: all extracted CUIs
  * See an example in the repository's [example directory](https://github.com/kpwhri/mml_utils/blob/master/examples/complete/mmlout/mml.mmi.csv)
* `notes.csv`: note-level information/counts about the notes in the corpus
  * See an example in the repository's [example directory](https://github.com/kpwhri/mml_utils/blob/master/examples/complete/mmlout/notes.mmi.csv)
* `cuis_by_doc.csv`: pivot table showing number of CUIs of each kind in a document
  * Each row represents a single input document
  * The columns are CUIs
  * Each value represents the count of CUIs in a particular row
  * See an example in the repository's [example directory](https://github.com/kpwhri/mml_utils/blob/master/examples/complete/mmlout/cui_by_doc.mmi.csv)

### Parameters

* `CORPUS_DIR`: path to files in the corpus that was processed
  * If more than one directory was used, supply them all as arguments
* `--outdir`: directory to write output to
* `--output-format`: extension of the file (i.e., for Metamap, use `mmi`)
* `--output-direcctory`: directory containing metamap's output `*.mmi` files
* `--cui-file`: (optional) file of 1 CUI per line to be extracted (all others will be ignored)
  * If you want CUIs to 'normalized' (where multiple CUIs might map to a single CUI), each row in the `cui_file` can contain two CUIs where the first, when identified, will be mapped to the second.
    * In the following lines, all instances of `C0012344` and `C0012345` will be mapped to `C0012344`.
      * `C0012344,C0012344`
      * `C0012345,C0012344`

### Example Config

Here's an example run on the command line, using the data generated by `config.toml` ([above](#example-configtoml)).

```
mml-extract-mml
C:\project\corpora\corpus1\files
--outdir
C:\project\extract\cuis
--cui-file
C:\project\cuis.txt
--output-format
mmi
--output-directory
C:\project\extract\mmout\rxnorm_mdr
```

This will generate the `mmi.csv`, `notes.csv`, and `cuis_by_doc.csv` files described above. (If the `cuis_by_doc.csv` file is absent, ensure that `pandas` is installed.)


## Run AFEP

If you are using Metamap to run the PheNorm algorithm (or another algorithm which also requires use of AFEP), then this section will guide you through the steps. When running AFEP, the goal is to select the set of features which occurs across multiple knowledge base source. If you are on this step, you have, presumably, already run Metamap on the text of these articles (and ensured that each article terminated in a newline).

To run AFEP, update the `run_afep-{datetime}.toml` file generated in the [Build Config Files section above](#build-config-files-and-shell-scripts). Running this will generate a series of CSV files with (as long as `build_summary` is set to `true`) a summarizing CSV file. You can use the `afep_summary.csv` (or `afep_summary.xlsx`) file to review and select a subset of CUIs for inclusion.

Once the set of CUIs has been identified, create a file called, e.g., `cuis.txt`, and place each CUI on a separate line. If you want to do CUI normalisation, place the `source CUI` (i.e., the CUI that is to be found in corpus) on the left, a comma, and then the `target CUI` (i.e., the CUI being mapped to) on the right.

Now, start from the beginning of this document to run Metamap on the entire corpus of notes. Then, when running `mml-extract-mml`, supply the `cuis.txt` as the `--include-cuis` parameter. This will extract only those CUIs identified by the AFEP process. 
