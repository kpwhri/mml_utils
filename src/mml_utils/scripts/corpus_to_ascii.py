"""
Certain programs like Metamap don't like UTF-8. This script will convert a corpus
    (or single file) from utf-8 (or other specified encoding) to ASCII

Usage:
    python corpus_to_ascii.py INDIR_utf8_corpus OUTDIR_ascii_corpus
"""
import re
from pathlib import Path

import click


@click.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.argument('outpath', type=click.Path(path_type=Path))
@click.option('--encoding', default='utf8', help='Source path encoding')
@click.option('--extension', default=None, help='Specify extension as glob pattern (e.g., *.txt)')
@click.option('--replacement', default=' ', help='Specify string to replace non-ASCII with.')
def _corpus_to_ascii(path: Path, outpath: Path, encoding='utf8', extension=None, replacement=' '):
    pat = re.compile(r'[^\x00-\x7f]')
    if path.is_dir():
        outpath.mkdir(exist_ok=True)
        for file in path.glob(extension or '*'):
            if file.is_dir():
                continue
            with open(file, encoding=encoding) as fh:
                text = fh.read()
            with open(outpath / file.name, 'w', encoding='ascii') as out:
                out.write(pat.sub(replacement, text))
    else:
        with open(path, encoding=encoding) as fh:
            text = fh.read()
        with open(outpath, 'w', encoding='ascii') as out:
            out.write(pat.sub(replacement, text))


if __name__ == '__main__':
    _corpus_to_ascii()
