"""
Split filelist into multiple parts
"""
import pathlib

import click


class MultiWriter:
    def __init__(self, file: pathlib.Path, n):
        self.filehandlers = []
        for i in range(n):
            self.filehandlers.append(open(f'{file}_part{i}', 'w', encoding='utf8'))

    def __enter__(self):
        return self

    def write(self, content, number):
        self.filehandlers[number].write(content)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for filehandler in self.filehandlers:
            filehandler.close()


@click.command()
@click.argument('filelist', type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
@click.argument('n', type=int)
def split_filelist(filelist: pathlib.Path, n: int):
    """
    Split filelist into n separate (and mostly equal) parts
    :param filelist:
    :param n:
    :return:
    """
    with MultiWriter(filelist, n) as writer:
        with open(filelist, encoding='utf8') as fh:
            for i, line in enumerate(fh):
                writer.write(f'{line.strip()}\n', i % n)


if __name__ == '__main__':
    split_filelist()
