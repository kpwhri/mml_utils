from pathlib import Path

import click
from loguru import logger

from mml_utils.config.build_mm_script import MultiBuildMMScript
from mml_utils.config.parser import parse_config
from mml_utils.build.mm_scripts import RotatingFileHandler, write_shell_script, write_ensure_directories
from mml_utils.phenorm.afep import write_afep_script_for_dirs


@click.command()
@click.argument('config_file', required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
def _run_build_mm_multi(config_file):
    """
    Use config file to guide
    :param config_file: currently only supports toml or json
    :return:
    """
    run_build_mm_multi(config_file)


def run_build_mm_multi(config_file):
    data = parse_config(config_file)
    config = MultiBuildMMScript(**data)
    target_dirs = set()
    with RotatingFileHandler(
            config.outpath, config.script_stem, max_per_script=config.max_per_script, num_scripts=config.num_scripts,
    ) as writer:
        for run in config.runs:
            logger.info(f'Running {run.name}...')
            target_dirs |= write_shell_script(writer, config.directory, config.filelist,
                                              mm_path=config.mm_path, mm_outpath=run.mm_outpath,
                                              parameters=run.parameters, replace=config.replace)
    logger.info(f'Writing ensure directories script...')
    write_ensure_directories(config.outpath, target_dirs)
    logger.info(f'Writing example AFEP config...')
    write_afep_script_for_dirs(config_file.parent, target_dirs, mml_format='mmi')
    logger.info(f'Completed.')


if __name__ == '__main__':
    _run_build_mm_multi()
