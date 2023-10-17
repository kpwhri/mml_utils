import click
from pathlib import Path

import unicodedata


@click.command()
@click.option('--filelist', default=None, type=click.Path(path_type=Path, dir_okay=False),
              help='File with list of all files to be cleaned, one per line. This or `--inpath` arg is required.')
@click.option('--inpath', default=None, type=click.Path(path_type=Path, file_okay=False),
              help='Directory with files to be cleaned. This or `filelist` arg is required.')
@click.option('--outpath', default=None, type=click.Path(path_type=Path, file_okay=False),
              help='Directory to write files to.')
@click.option('--from-encoding', default=None,
              help='Source encoding.')
@click.option('--to-encoding', default='latin1',
              help='Encoding to write output to.')
def clean_files_cmd(filelist: Path = None, inpath: Path = None, outpath: Path = None, from_encoding=None,
                    to_encoding='latin1'):
    if not filelist and not inpath:
        raise ValueError('Either `filelist` or `inpath` must be specified.')
    if filelist:
        if not outpath:
            outpath = filelist.parent / 'cleaned'
        outfilelist = filelist.parent / f'cleaned_{filelist.name}'
        outpath.mkdir(exist_ok=True)
        with open(filelist) as fh:
            with open(outfilelist, 'w') as out:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    path = Path(line)
                    with open(outpath / path.name, 'w', encoding=to_encoding, errors='ignore') as out_txt:
                        out_txt.write(clean_file(path, encoding=from_encoding))
                    out.write(f'{(outpath / path.name).as_posix()}\n')
    elif inpath:
        if not outpath:
            outpath = inpath.parent / 'cleaned'
        outpath.mkdir(exist_ok=True)
        for file in inpath.iterdir():
            with open(outpath / file.name, 'w', encoding=to_encoding, errors='ignore') as out:
                out.write(clean_file(file, encoding=from_encoding))


def clean_file(file, encoding=None):
    with open(file, encoding=encoding) as fh:
        text = remove_control_characters(fh.read())
        if not text.rstrip(' ').endswith('\n'):
            text += '\n'
    return text


def remove_control_characters(s):
    return ''.join(ch for ch in s
                   if ch == '\n'  # keep line endings
                   or unicodedata.category(ch)[0] != 'C'  # skip other control characters
                   )


if __name__ == '__main__':
    clean_files_cmd()
