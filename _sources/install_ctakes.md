
# Installing cTAKES

These steps focus on install cTAKES for running `ctakes-fast` on Windows.

## In Brief

This will summarize the steps from the [cTAKES User Install Guide](https://cwiki.apache.org/confluence/display/CTAKES/cTAKES+4.0+User+Install+Guide).

1. Navigate to https://ctakes.apache.org/downloads.cgi and download appropriate files.
   * Click 'Windows' button under `User Installation`
   * To update dictionary (but not cTAKES, you can download new dictionary):
     * Click 'Fast Version' button under `UMLS Dictionary`
     * (Optional) Click 'All Versions' button under `UMLS Dictionary`
2. Unzip `apache-ctakes-x.y.z.a` to CTAKES_HOME (e.g., `C:\apache-ctakes`)
   * (Optional) Unzip `ctakes-resources-x.y-bin`, and move contents of `resources` directory into `CTAKES_HOME/resources`.
3. [Obtain UMLS Key](umls_license.md#obtain-umls-key)
4. (Optional) Add the api key as a user environment variable (i.e., not shared with other users)
   * Start > Environment variables. Under `User Variables`, `New`. Set `umlsKey` to your API KEY.
   * In powershell, add to your `.profile`: `$env:umlsKey='API-KEY'`
5. Test run with these commands (in, e.g., powershell) -- pick a directory with a single file:
   * `cd CTAKES_HOME`
   * `bin\runClinicalPipeline -i C:\Input\MyNotes\ --xmiOut C:\Output\MyNotes\ --key API-KEY`
6. You can ensure that `fast-ctakes` is being run by looking for the logging info line 'Dictionary Descriptor' which should reference `/lookup/fast/sno_rx_##aa.xml`.
