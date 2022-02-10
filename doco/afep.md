# Automated Feature Extraction for Phenotyping (AFEP)

## About AFEP

AFEP (Automated Feature Extraction for Phenotyping) is a component of the phenotyping algorithm PheNORM which attempts
to automatically determine useful features by mining knowledge base articles like Wikipedia, Medline, etc.

* See the paper [on pubmed](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4986664/)

## Steps

This is not directly related to MML, but MetaMapLite can be used to extract concepts for use in extracting concepts for
MetaMapLite. These steps will guide you through extracting the concepts of interest as well as processing them using
the [`mml_utils` package](https://github.com/kpwhri/mml_utils).

```{admonition} NLP Tool for Concept Extraction
The authors recommend NILE, but this is
closed source, difficult to get, not clearly version (i.e., impossible to update), and doesn't seem to have had any work
done in a few years...so probably moribund, unfortunately.

Other options include:
* cTAKES
* MetaMap
* MetaMapLite
* Your own custom tool ;)
```

1. Download text from Knowledge Base sources (e.g., Medline, Medscape, Merck, Wikipedia, Mayo) on your target
   condition (e.g., arthritis or COVID-19).
2. Name these text files something like 'Medscape.txt' and 'Wikipedia.txt' and place them in a new directory (
   e.g., `/kb_articles/`).
3. Split the files into no more than say 200 lines (
   see [mml-split-files](https://github.com/kpwhri/mml_utils#mml-split-files) command for assistance).
4. Run MML on the entire directory (e.g., `/kb_articles/`).
5. Run [mml-run-afep](https://github.com/kpwhri/mml_utils#mml-run-afep) on the output (see parametrisation there or
   below).

As a prerequisite, you'll need to install pandas (`pip install pandas`) which is not installed by default due to this
being the only script requiring it.

    mml-run-afep /kb_articles/ [--mml-format json|mmi] [--outdir .]