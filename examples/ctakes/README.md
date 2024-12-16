
# cTAKES

How to run with cTAKES.

## Prerequisites

* Download/unpack cTAKES
  * For the examples below, assume that the version was `apache-ctakes-4.0.0.1` and was unzipped into `C:\ctakes`, such that the folder `C:\ctakes\apache-ctakes-4.0.0.1` exists
  * We'll call `C:\ctakes\apache-ctakes-4.0.0.1` CTAKES_HOME, and this must contain the `bin` directory
* Download/unpack cTAKES dictionary
  * Suppose you downloaded version `ctakes-resources-4.0-bin`. This contains a `resources` folder. Copy-paste the contained `resources` folder into CTAKES_HOME (thereby merging the `resources` folders).
* Have a UMLS API key
  * Get this UUID by logging into your UTS Profile: https://uts.nlm.nih.gov/uts/profile
* Install `mml_utils`
  * `git clone https://github.com/kpwhri/mml_utils`
  * `cd mml_utils`
  * `pip install .`

## Running

cTAKES operates with directories. Thus, you will have files in an input directory (e.g., `C:\notes`) and write the output as `.xmi` files to an output directory (e.g., `C:\ctakes_out`). If an input file is `C:\notes\001.txt`, the output file will be `C:\ctakes_out\001.txt.xmi`.

If you wish to enable 'multi-processing', you'll need to move files into multiple directories (e.g., move 25% to each of `C:\notes0`, `C:\notes1`, etc.). Note that the `mml-extract-mml` only works with a single output directory. Either plan to run multiple `mml-extract-mml` processes (appending the results), or dump into a single output directory. In addition, multiple cTAKES installs will be required as the application places a lock on the dictionary. The same configuration (i.e., `ctakes` directory) can be moved to separate machines or duplicated on the same machine to get around the lock.

Command:

    mml-run-ctakes [INPUT_DIRECTORY] --ctakes-home [CTAKES_HOME] --outdir [OUTPUT_DIRECTORY] --umls-key [UMLS KEY] --dictionary [DICTIONARY_XML_FILE]

For example:

    mml-run-ctakes C:\notes --ctakes-home C:\ctakes\apache-ctakes-4.0.0.1 --outdir C:\ctakes_out --umls-key 752a91b2-5dc9-fake-aa41-ecfd88dbb90a --dictionary C:\ctakes\apache-ctakes-4.0.0.1\resources\org\apache\ctakes\dictionary\lookup\fast\sno_rx_16ab.xml

This command with run the `bin\runClinicalPipeline.bat` or `bin/runClinicalPipeline.sh` file. If there are issues with the run, this file can often be directly edited (or directly initialized and avoid using `mml_utils`).

## Extracting Results

Once cTAKES has run, we'll need to extract the relevant CUIs from the output. To accomplish this, we'll use the `mml-extract-mml` command (this is the same command and parameters as for extracting with MetaMapLite and MetaMap).

    mml-extract-mml C:\notes --outdir C:\extract_cuis --cui-file C:\cuis.txt --extract-format xmi --extract-directory C:\ctakes_out [--extract-encoding utf8]

* `cuis.txt`: a single CUI per line, only these CUIs will be considered

If you are checking progress (and expect a number of files to be unprocessed) run `mml-extract-mml` with `--skip-missing` flag, OR:

    mml-extract C:\ctakes_out --outdir C:\extract_cuis_incomplete --cui-file C:\cuis.txt --extract-format xmi --note-directory C:\notes

If you have multiple notes directories that were run in parallel, you can extract all of these at once (NB: be suer to keep the notes directories and extract directories in order to speed up processing):

    mml-extract-mml C:\notes0 C:\notes1 --outdir C:\extract_cuis --cui-file C:\cuis.txt --extract-format xmi --extract-directory C:\ctakes_out0 --extract-directory C:\ctakes_out1 [--extract-encoding utf8]


## Troubleshooting

### Heap Space Error

* consider increasing integer value in bin\runClinicalPipeline.bat: `-Xmx2g`

### trying to serialize non-XML character

There's a non-XML character in your file. Try re-running using the same command line, but add `--clean-files` which will remove XML characters.

