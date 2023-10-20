from datetime import datetime
from pathlib import Path


def build_filelist(path: Path, outpath: Path = None, extensions: set = None) -> Path:
    if outpath is None:
        outpath = path.parent
    filelist_path = outpath / f'filelist_auto_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(filelist_path, 'w') as out:
        if path.is_file():
            out.write(f'{path.absolute()}\n')
        else:
            for file in path.iterdir():
                if file.is_dir():
                    continue
                if extensions and file.suffix not in extensions:
                    continue
                if not extensions and file.suffix and file.suffix != '.txt':
                    continue
                out.write(f'{file.absolute()}\n')

    return filelist_path
