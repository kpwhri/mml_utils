from pathlib import Path

from pydantic import BaseModel


class BuildMMScript(BaseModel):
    parameters: str = ''
    mm_outpath: Path = None
    name: str = ''

    def set_mm_outpath(self, mm_outpath: Path):
        if not self.mm_outpath:
            self.mm_outpath = mm_outpath / self.name

    def add_parameters(self, parameters):
        """Add shared parameters"""
        self.parameters = f'{parameters} {self.parameters}'


class MultiBuildMMScript(BaseModel):
    runs: list[BuildMMScript]
    outpath: Path = Path('.')  # outpath where scripts will be written
    mm_path: Path | str = None  # path to metamap exe, defaults to assuming on path
    filelist: Path = None  # filelist with files to be processed by MM
    directory: Path = None  # directory containing source files to be processed
    mm_outpath: Path = None  # outpath for metamap mmi files
    script_stem = 'script'  # name for generated scripts
    num_scripts = -1
    max_per_script = -1
    parameters = ''  # shared parameters
    replace: tuple[str, str] = None  # e.g., Windows path to mount: ['M:', '/mnt/m']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # post init
        if self.filelist is None and self.directory is None:
            raise ValueError(f'Either `filelist` or `directory` must be specified.')

        if isinstance(self.mm_path, Path):
            self.mm_path = self.mm_path.as_posix()
        elif self.mm_path is None:
            self.mm_path = 'metamap'

        if not self.outpath:
            self.outpath = Path('.')
        self.outpath.mkdir(exist_ok=True)

        # check runs
        parameters = dict()
        names = set()
        for run in self.runs:
            run.set_mm_outpath(self.mm_outpath)
            run.add_parameters(self.parameters)
            if run.parameters in parameters:
                raise ValueError(f'Duplicate parameters found in config: '
                                 f'{run.parameters} found in {run.name} and {parameters[run.parameters]}')
            if run.name in names:
                raise ValueError(f'Duplicate names found in config: {run.name}, all names must be unique.')
            parameters[run.parameters] = run.name
            names.add(run.name)
