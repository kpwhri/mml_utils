
# Instructions for Installing Metamap on Windows

These steps focus on Windows, as the Linux case is well-documented.

## Prerequisites

* Install `wsl` (Windows Subsystem for Linux)
  * Install a distro (e.g., Ubuntu LTS)
  * Update packages: `sudo apt-get update`
  * Ensure java installed
    * Run `java` and pick an option 
    * `default_jre` will probably work, I used `sudo apt install openjdk-11-jre-headless`
* Downloads require [UMLS License](umls_license.md)
* Download bzip file to install MetaMap: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/run-locally/MainDownload.html
* Download web api: https://lhncbc.nlm.nih.gov/ii/tools/Web_API_Access.html
* Install [UMLS Metathesaurus](install_umls.md)

## Install Metamap

1. Unzip downloaded `public_mm_linux_*.bz2` file (do this, e.g., with 7-zip)
   * Place the resulting `public_mm` in, e.g., `C:\`
2. Prepare paths
   * `export JAVA_HOME=/usr/bin/java` (determine path using `which java`)
   * `export PATH=$PATH:/mnt/c/public_mm/bin`
3. Run install scripts
   * `cd /mnt/c/public_mm`
   * `./bin/install.sh`
     * Confirm `JAVA_HOME` and `PATH` (should be able to just click `enter`)
     * If permission denied, try again with `sudo ./bin/install.sh`
4. Start POS and WSD servers
   * Start POS tagger: `./bin/skrmedpostctl start`
   * Start WSD server: `./bin/wsdserverctl start`
   * NB: to stop the severs, run above command with `stop` instead of `start`
5. Test the installation
   * `./bin/metamap`

## Download Datasets

Datasets can be downloaded from: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/additional-tools/DataSetDownload.html

To access something like MedDRA, download the 'NLM' version which includes the full metathesaurus.

For using MedDRA:

* Download NLM version (both common model and either strict or relaxed)
* `cd /mnt/c/`
  * There should be a `public_mm` folder in here
* Unpack base, AND relaxed and/or strict (base cannot run on its own)
  * `sudo tar xvfj /path/to/public_mm_data_nlm_YYYYaa_base.tar.bz2`
  * `sudo tar xvfj /path/to/public_mm_data_nlm_YYYYaa_relaxed.tar.bz2`
  * `sudo tar xvfj /path/to/public_mm_data_nlm_YYYYaa_strict.tar.bz2`
* If the year `YYYY` is different between this and the default, download an updated specialist lexicon (at the top of the additional tools page)
  * `sudo tar xvfj /path/to/public_mm_data_dblexicon_YYYY.tar.bz2`
* If you haven't already, restart the servers

## Run Metamap

The following will assume that the desired use case is `NLM` (specifically, MDR/Meddra) with the '2022AB' release. A complete documentation of the command line parameters are available here: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/MM09_Usage.html

* Launch part of speech and word sense disambiguation servers:
  * `./bin/skrmedpostctl start`
  * `./bin/wsdserverctl start`
* Run:
  * `echo "lung cancer" | metamap -R MDR -V NLM -Z 2022AB`
    * add `-C` for relaxed model (strict model is used by default, or use `-A`)
* Run on Files:
  * `metamap -R MDR -V NLM -Z 2022AB <INPUT_FILEPATH> <OUTPUT_FILEPATH>`

```{admonition} Files run with Metamap Must End in a Newline
All files read by Metamap must end in a newline (\n), otherwise they will not be correctly processed and raise an error. If you open the file in an editor, ensure that the last line is empty/blank.
```

## Troubleshooting

### `db_open_problem ---> .../norm_prefix`

You probably don't have the appropriate lexicon downloaded. To confirm, go to the directory (`...` above) and run `ll`.

#### Resolution

* Get the correct year Specialist Lexicon from: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/additional-tools/DataSetDownload.html

### `fgets: No such file or directory`

If you're in Windows on WSL, you probably unpacked the `tar.bz2` archive using a program on Windows like 7-zip. This caused the symbolic links to fail to be created.

#### Resolution

* Unpack in WSL using the command:
  * `sudo tar xvfj /path/to/public_mm_....tar.bz2`
