from pathlib import Path


class RotatingFileHandler:

    def __init__(self, path, stem, max_per_script=-1, num_scripts=-1):
        self.path = path
        self.stem = stem
        self.fhs = []
        self.n = 0
        self.count = 0
        self.max_per_script = max_per_script
        self.num_scripts = num_scripts
        self.is_max_per_script = max_per_script > -1  # simplify this repeated check
        self._init_filehandlers()

    def next_script(self):
        """Get path to next script."""
        path = self.path / f'{self.stem}_{self.n}.sh'
        self.n += 1
        return path

    def _init_filehandlers(self):
        if self.is_max_per_script:
            self.fhs.append(open(self.next_script(), 'w', newline=''))
        else:
            if self.num_scripts == -1:
                self.num_scripts = 1
            for _ in range(self.num_scripts):
                self.fhs.append(open(self.next_script(), 'w', newline=''))

    def rotate(self):
        """Rotate output script"""
        for fh in self.fhs:
            fh.close()
        self.fhs = [open(self.next_script(), 'w', newline='')]

    def writeline(self, line):
        self.count += 1
        if self.is_max_per_script:
            if self.count >= self.max_per_script:
                self.count = 0
                self.rotate()
            self.fhs[0].write(f'{line}\n')
        else:  # num_scripts
            self.fhs[self.count % self.num_scripts].write(f'{line}\n')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for fh in self.fhs:
            fh.close()


def get_next_file(filelist: Path = None, directory: Path = None):
    """Given a filelist or directory, yield the next item"""
    if filelist:
        with open(filelist) as fh:
            for line in fh:
                yield Path(line.strip())
    elif directory:
        for file in directory.iterdir():
            yield file


def build_mm_script(parameters='', outpath: Path = None, mm_path: Path = None, filelist: Path = None,
                    directory: Path = None, mm_outpath: Path = None,
                    script_stem='script', num_scripts=-1, max_per_script=-1):
    if filelist is None and directory is None:
        raise ValueError(f'Either `filelist` or `directory` must be specified.')

    mm_path = str(mm_path) if mm_path else 'metamap'
    if not outpath:
        outpath = Path('.')
    outpath.mkdir(exist_ok=True)

    with RotatingFileHandler(outpath, script_stem, max_per_script=max_per_script, num_scripts=num_scripts) as writer:
        target_dirs = write_shell_script(writer, directory, filelist, mm_outpath, mm_path, parameters)

    write_ensure_directories(outpath, target_dirs)


def write_ensure_directories(outpath, target_dirs):
    with open(outpath / 'ensure_directories.sh', 'w', newline='') as out:
        out.write(f'# Run this file to ensure all output directories have been created.\n')
        for target_dir in target_dirs:
            out.write(f'mkdir -p {target_dir.as_posix()}\n')


def write_shell_script(writer, directory, filelist, mm_outpath, mm_path, parameters):
    target_dirs = set()
    for target_file in get_next_file(filelist, directory):
        target_dir = mm_outpath or target_file.parent
        target_dirs.add(target_dir)
        writer.writeline(
            f'{mm_path} {parameters} {target_file.as_posix()} {(target_dir / target_file.stem).as_posix()}.mmi'
        )
    return target_dirs
