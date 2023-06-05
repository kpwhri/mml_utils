"""
Run AFEP greedy algorithm on results of MetaMapLite extraction of Raw Knowledge Base files.

Implementation notes:
1. Only json currently implemented (not mmi)
2. CUIs will be grouped by article type.
    * Article type is defined as all content before the first '_' (not including extension)..
"""
import pathlib

import click

from mml_utils.phenorm.afep import run_afep_algorithm


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--mml-format', type=str, default='json',
              help='Output format to look for (e.g., "json" or "xmi"). "mmi" currently not implemented.')
@click.option('--outdir', type=click.Path(file_okay=False, path_type=pathlib.Path), default=None,
              help='Output directory')
@click.option('--expand-cuis', is_flag=True,
              help='For CUIs with and/or, look for subterms. This helps to comabat longest match in, e.g., MML.')
@click.option('--apikey', default=None, type=str,
              help='API key for use when trying to expand CUIs.')
@click.option('--skip-greedy-algorithm', is_flag=True, default=False,
              help='Skip greedy selection algorithm.')
@click.option('--min-kb', default=None, type=int,
              help='Minimum number of knowledge base articles. Defaults to half (rounded up) of KB sources.')
@click.option('--max-kb', default=None, type=int,
              help='Maximum number of knowledge base articles. No default (max will not be enforced).')
@click.option('--data-directory', type=click.Path(exists=True, path_type=pathlib.Path), multiple=True,
              help='Data directory if data is in a different directory than notes (e.g., with cTAKES).')
def _run_afep_algorithm(note_directories, *, mml_format='json', outdir: pathlib.Path = None,
                        expand_cuis=False, apikey=None, skip_greedy_algorithm=False, min_kb=None, data_directory=None):
    """
    Run greedy AFEP algorithm on extracted knowledge base articles

    :param expand_cuis:
    :param apikey:
    :param skip_greedy_algorithm:
    :param outdir:
    :param note_directories:
    :param mml_format:
    :return:
    """
    run_afep_algorithm(note_directories, mml_format=mml_format, outdir=outdir, expand_cuis=expand_cuis, apikey=apikey,
                       skip_greedy_algorithm=skip_greedy_algorithm, min_kb=min_kb, data_directory=data_directory)


if __name__ == '__main__':
    _run_afep_algorithm()
