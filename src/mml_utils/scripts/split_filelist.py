"""
Split filelist into multiple parts
"""
import pathlib

import click
from loguru import logger


class MultiWriter:
    def __init__(self, file: pathlib.Path, n):
        self.filehandlers = []
        self.counts = []
        for i in range(n):
            self.filehandlers.append(open(f'{file}_part{i}', 'w', encoding='utf8'))
            self.counts.append(0)

    def __enter__(self):
        return self

    def write(self, content, number):
        self.filehandlers[number].write(content)
        self.counts[number] += 1

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
    total_rows = 0
    with MultiWriter(filelist, n) as writer:
        with open(filelist, encoding='utf8') as fh:
            for i, line in enumerate(fh):
                total_rows += 1
                writer.write(f'{line.strip()}\n', i % n)
        logger.info(f'Divided {total_rows} into {n} separate files: {writer.counts} ({sum(writer.counts)})')


if __name__ == '__main__':
    split_filelist()
