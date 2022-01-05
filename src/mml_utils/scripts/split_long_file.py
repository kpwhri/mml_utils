"""
MML seems to have trouble with longer files. Split these up but preserve the offsets (if possible).

I am not clear if this is based on line number or character count.
"""
import pathlib

import click


@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
@click.option('--n-lines', type=int, default=200,
              help='Number of lines after which to create a new file.')
@click.option('--filelist', type=click.Path(dir_okay=False, path_type=pathlib.Path),
              help='Choose to create a particularly-named filelist. All content will be appended.')
def split_files_on_lines(files: list[pathlib.Path], n_lines=200, *, encoding='cp1252', filelist=None):
    if not filelist:
        filelist = files[0].parent / f'filelist_split_{files[0].stem}.txt'
    with open(filelist, 'a', encoding=encoding) as filelist_out:
        for file in files:
            for name in split_on_lines(file, n_lines=n_lines, encoding=encoding):
                filelist_out.write(f'{name}\n')


def split_on_lines(file, n_lines=200, *, encoding='cp1252'):
    lines = []
    i = 0
    with open(file, encoding=encoding) as fh:
        for line in fh:
            lines.append(line)
            if len(lines) % n_lines == 0:
                name = file.parent / f'{file.stem}_{i}{file.suffix}'
                with open(name, 'w', encoding=encoding) as out:
                    out.writelines(lines)
                yield name
                i += 1
                lines = []


if __name__ == '__main__':
    split_files_on_lines()
