# Using MetaMapLite

* The README will include the most up-to-date information, but it can be a bit light on examples.
* The current version of the README (as of this writing) is [online](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/README_MetaMapLite_3.6.2rc5.html)
    * See 'Current options' for the list of available options.

## Example Usage

Here are some example for using MetaMapLite. All these should be run from inside the `public_mm_lite` directory.

### Run against a list of files, output as `json`.

* Note that the output will be in the same directory. If a file is called `0001.txt`, the output will be `0001.json`.
* `--usecontext` will determine negation based on the context algorithm rather than negex
* Only the semantic types `[topp]`, `[fndg]`, `[dsyn]`, `[sosy]`, and `[lbpr]` will be included in the output.

```shell
metamaplite.bat --filelistfn=filelist.txt --outputformat=files --usecontext --restrict_to_sts=topp,fndg,dsyn,sosy,lbpr
```

```{admonition} Re-running MetaMapLite
To re-run on the same files, you will need to include an `--overwrite` flag to tell MML that it's okay to overwrite the existing output files.
```

```{admonition} Negation and JSON Output
Currently, `json` files do not output negation information, but you can make the following change to get that information: [https://github.com/lhncbc/metamaplite/pull/16](https://github.com/lhncbc/metamaplite/pull/16).
```

### Run/test text directly in the shell:

* `echo "asymptomatic patient populations" | .\metamaplite.bat --pipe --outputformat=json`