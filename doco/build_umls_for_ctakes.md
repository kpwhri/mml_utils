
# Build UMLS for cTAKES

By default, cTAKES includes the `SNOMED_CT` and `RXNORM` subsets, but sometimes this isn't sufficient. You may require `MedDRA` or any other number of UMLS sources.



## Prerequisites

* Download the full UMLS: [Install UMLS Metathesaurus](install_umls.md#download-full-umls)
* Downloaded cTAKES and unzip directory. This base directory will be called `CTAKES_HOME` (e.g., C:\apache-ctakes-4.x.y.z)

## Steps to Build Dictionary

The main documentation is on the cTAKES wiki: https://cwiki.apache.org/confluence/display/CTAKES/Dictionary+Creator+GUI

* Launch Dictionary Creator GUI window
  * `cd $CTAKES_HOME`
  * `bin\runDictionaryCreator.bat`  (or `.sh`)
* On the `UMLS Installation` line, choose `Select Directory` button.
* Choose a UMLS download directory (it should contain a folder called `META`)
  * In whatever shell you ran the command, you can watch the vocabularies get loaded
* In the GUI, the left hand side shows available [source vocabularies](glossary.md#umls-dataset-levels). On the right hand side, semantic types can be selected/unselected.
  * To include a particular vocabulary, place a checkcbox next to it.
    * To remove a vocabulary, first ensure the 'Source' is checked, and then uncheck 'Target' first; then, uncheck 'Source'
  * To include/exclude a particular semantic type, choose the checkbox next to it.
  * The GUI window can be expanded to see more elements.
  * To see all the checkboxes, sort by the 'Source' or 'Use' columns (click the column header)
  * To replicate MetaMapLite, choose the vocabularies level 0, 4, and 9 (https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html) and all semantic types.
* Once the appropriate source vocabularies and semantic types have been selected:
  * Name the dictionary something useful (and memorable) in the `Dictionary Name` line
    * Ideally, include a reference to the vocabularies, the purpose, as well as the UMLS version
  * Choose 'Build Dictionary'
* You dictionary will be created in `$CTAKES_HOME\resources\org\apache\ctakes\dictionary\lookup\fast`

## Run cTAKES with New Dictionary

If already running with `bin\runClinicalPipeline.bat` (or `.sh`):
* Add the `--lookupXml` option to specify the full path
* E.g., 
```
.\bin\runClinicalPipeline.bat 
-i C:\inputfiles 
--xmiOut C:\outputxmi 
--key xxx-yyy 
--lookupXml C:\ctakes\apache-ctakes-4.x.y.z\resources\org\apache\ctakes\dictionary\lookup\fast\custom_dict.xml
```

If using MML Utils' `run_ctakes` command, 
* Add `--dictionary` to the existing command
* E.g.,
```
mml-run-ctakes 
C:\inputfiles 
--ctakes-home C:\ctakes\apache-ctakes-4.x.y.z 
--outdir C:\outputxmi 
--umls-key xxx-yyy 
--dictionary C:\ctakes\apache-ctakes-4.x.y.z\resources\org\apache\ctakes\dictionary\lookup\fast\custom_dict.xml
```
