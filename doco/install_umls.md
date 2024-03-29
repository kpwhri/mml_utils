
# Install UMLS Metathesaurus

There are several methods depending on what you want to download (though they all include mostly the same steps).

It is worth mentioning that soon dictionary creation might be configurable online (rather than requiring download first). 

## Download

### Download Full UMLS

For many applications, the entire UMLS must be downloaded. This can take a while as the files are quite large.

* Navigate to https://uts.nlm.nih.gov/uts/ and login
  * If you don't yet have a login, [register](umls_license.md#create-umls-account)
* Under the 'UMLS' section, choose `Download`
  * Or, from the top menu, select `Download` > `UMLS`.
* To download a dataset that can be customized (e.g., select only `MedDRA`), in the second table, download `Full UMLS Release Files` (~30GB).
* Download to a location like the Downloads folder
* Unzip the file to `C:\umls\umls\-202xAA`

### Download MRCONSO File

Often, all that is required (especially for something like `cTAKES`) is the `MRCONSO.RRF` file.

* Navigate to https://uts.nlm.nih.gov/uts/ and login
  * If you don't yet have a login, [register](umls_license.md#create-umls-account)
* Under the 'UMLS' section, choose `Download`
  * Or, from the top menu, select `Download` > `UMLS`.
* In the section for the most recent dataset, download `MRCONSO.RRF`
* Download to a location like the Downloads folder
* Unzip the file to `C:\umls\umls-202xAA-mrconso`


## Install Custom Subset with Metamorphosys

Install a hand-selected subset of the UMLS. This requires the 'Full UMLS Release Files' which includes Metamorphosys.

* Download a version of UMLS including Metamorphosys
* Unzip the downloaded archive
* Open the directory, and unzip `mmsys.zip` (this contains the Metamorphosys binary)
* Run the executable
* Select the relevant subset

## Using Subset
