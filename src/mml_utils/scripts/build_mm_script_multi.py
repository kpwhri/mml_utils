from pathlib import Path

import click
from loguru import logger

from mml_utils.config.build_mm_script import MultiBuildMMScript
from mml_utils.config.parser import parse_config
from mml_utils.build.mm_scripts import RotatingFileHandler, write_shell_script, write_ensure_directories
from mml_utils.os_utils import escape_space
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
    example_usage = escape_space((config.outpath / config.script_stem).as_posix())
    if config.replace:
        example_usage = example_usage.replace(config.replace[0], config.replace[1])
    with RotatingFileHandler(
            config.outpath, config.script_stem, max_per_script=config.max_per_script, num_scripts=config.num_scripts,
            header_rows=[f'# Usage: {example_usage}_n.sh', '# mount -t drvfs C: /mnt/c'],
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
    logger.info(f'To access script directory, try:')
    logger.info(f' * `cd {example_usage.rsplit("/", 1)[0]}`')
    if example_usage.startswith('/mnt'):
        mnt_path = '/'.join(example_usage.split('/')[:3])
        logger.info(f'On WSL, you may first need to mount the drives:')
        logger.info(f' * `mkdir {mnt_path}`')
        logger.info(f' * `mount -t drvfs {config.outpath.drive} {mnt_path}`')


if __name__ == '__main__':
    _run_build_mm_multi()
