import os
from pathlib import Path
import shutil
import subprocess
from string import Template

from loguru import logger

from mml_utils.os_utils import get_cp_sep, is_windows

LOG4J_CONFIG = Template('''<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="$LOGLEVEL">
  <Appenders>
    <File name="MetaMapLitePipeline" fileName="logs/MetaMapLiteDebug.log" append="false">
      <PatternLayout pattern="%t %-5p %c{2} - %m%n"/>
    </File>
    <Console name="STDOUT" target="SYSTEM_OUT">
      <PatternLayout pattern="%d %-5p [%t] %C{2} (%F:%L) - %m%n"/>
    </Console>
  </Appenders>
  <Loggers>
    <Logger name="org.apache.log4j.xml" level="$LOGLEVEL">
      <AppenderRef ref="MetaMapLitePipeline"/>
    </Logger>
    <Root level="$LOGLEVEL">
      <AppenderRef ref="MetaMapLitePipeline"/>
    </Root>
  </Loggers>
</Configuration>''')


def get_env(mml_home: Path):
    return {
        'PROJECTDIR': str(mml_home),
        'OPENNLP_MODELS': str(mml_home / 'data' / 'models'),
        'CONFIGDIR': str(mml_home / 'config'),
    }


def get_mml_jar(mml_home: Path):
    file = next((mml_home / 'target').glob('*-standalone.jar'))
    return file


def get_umls_versions(cwd: Path):
    versions = [p for p in cwd.iterdir() if p.is_dir()]
    options = []
    for version in versions:
        for dataset in version.iterdir():
            if dataset.is_dir():
                options.append((version.stem, dataset.stem))
    return sorted(options, reverse=True)


def run_mml(filename, cwd: Path, *, output_format='files', restrict_to_sts=None, restrict_to_src=None,
            property_file=None, properties=None, is_filelist=True, version=None, dataset='USAbase',
            loglevel='WARN'):
    restrict_to_sts = f"--restrict_to_sts={','.join(restrict_to_sts)}" if restrict_to_sts else ''
    restrict_to_src = f"--restrict_to_sources={','.join(restrict_to_src)}" if restrict_to_src else ''

    # handle properties
    property_file = f'-Dmetamaplite.property.file={property_file}' if property_file else ''

    # handle version/dataset
    installed_versions = get_umls_versions(cwd / 'data' / 'ivf')
    if version is None or (version, dataset) not in installed_versions:
        logger.warning(f'UMLS Version and/or Dataset NOT SPECIFIED or NOT FOUND!')
        logger.warning(f'> Version: {version}, Dataset: {dataset}')
        logger.info(f'Installed datasets/versions (in {cwd / "data" / "ivf"}:')
        for version_, dataset_ in installed_versions:
            selected_version = ''
            if dataset_ == dataset:
                version = version_
                selected_version = ' <<- Using this version as best match.'
            logger.info(f'> Version: {version_}, Dataset: {dataset_}{selected_version}')
    if version is None or not (cwd / 'data' / 'ivf' / version / dataset).exists():
        raise ValueError(f'UMLS Version/Dataset does not exist: {version}/{dataset}.')

    # handle log4j config
    log4j_config_file = cwd / 'config' / f'log4j2-{loglevel}.xml'
    if not log4j_config_file.exists():
        with open(log4j_config_file, 'w') as out:
            out.write(LOG4J_CONFIG.substitute(LOGLEVEL=loglevel.lower()))

    # list default properties
    default_props = (
        ('opennlp.en-sent.bin.path', cwd / 'data' / 'models' / 'en-sent.bin'),
        ('opennlp.en-token.bin.path', cwd / 'data' / 'models' / 'en-token.bin'),
        ('opennlp.en-pos.bin.path', cwd / 'data' / 'models' / 'en-pos-perceptron.bin'),
        ('opennlp.en-chunker.bin.path', cwd / 'data' / 'models' / 'en-chunker.bin'),
        ('log4j.configurationFile', log4j_config_file),
        ('metamaplite.log4jconfig', log4j_config_file),
        ('metamaplite.entitylookup.resultlength', '1500'),
        ('metamaplite.index.directory', cwd / 'data' / 'ivf' / version / dataset),
        ('metamaplite.excluded.termsfile', cwd / 'data' / 'specialterms.txt'),
    )
    found_props = set()
    prop_strings = []
    for key, value in (properties or ()) + default_props:
        if key in found_props:
            continue
        prop_strings.append(f'-D{key}={value}')
        found_props.add(key)
    properties = ' '.join(prop_strings)

    # JVM options
    jvm_opts = '-Xmx12g'
    # jvm_opts = '-Xmx1024m'  # 32 bit max
    classpath = get_cp_sep().join(str(x) for x in [
        cwd / 'target' / 'classes',
        cwd / 'build' / 'classes',
        cwd / 'classes',
        cwd,
        get_mml_jar(cwd),
    ])

    # metamaplite
    logger.info(f'Running Metamaplite on current set (install location: {cwd})')
    if is_windows():  # must have quotes in classpath
        prefix = f'java {jvm_opts} {property_file} {properties} -cp "{classpath}" gov.nih.nlm.nls.ner.MetaMapLite'
    else:  # cannot have quotes in classpath (ClassNotFoundException)
        prefix = f'java {jvm_opts} {property_file} {properties} -cp {classpath} gov.nih.nlm.nls.ner.MetaMapLite'
    file_arg = '--filelistfn' if is_filelist else '--filelist'
    cmd = (f'{prefix} {file_arg}={filename} --outputformat={output_format}'
           f' --overwrite --usecontext {restrict_to_sts} {restrict_to_src}'
           f''.split()
           )
    logger.debug('Running command >> ' + ' '.join(cmd))
    res = subprocess.run(cmd, universal_newlines=True, cwd=cwd, env=os.environ | get_env(cwd),
                         # stderr=subprocess.PIPE  # TODO: this will collect all logging and send to stderr
                         )
    if res.returncode != 0:
        logger.warning(f'Metamaplite returned with status code {res.returncode}.')
        logger.info(f'MML STDERR: {res.stderr}')
        logger.info(f'If no stderr, consider re-running with DEBUG mode.')
    return res


def repeat_run_mml(filename, cwd, *, output_format='files', restrict_to_sts=None, max_retry=10,
                   property_file=None, properties=None, version=None, dataset='USAbase',
                   loglevel='WARN', **kwargs):
    filelist_version = 0
    return_code = 1
    total_completed = 0
    error_path = Path(filename).parent / 'errors.txt'

    orig_filename = filename
    filename = f'{orig_filename}_{filelist_version}'
    shutil.copy(orig_filename, filename)

    res = None
    while return_code != 0:
        res = run_mml(
            filename,
            cwd,
            output_format=output_format,
            restrict_to_sts=restrict_to_sts,
            property_file=property_file,
            properties=properties,
            version=version,
            dataset=dataset,
            loglevel=loglevel,
        )
        return_code = res.returncode
        if return_code == 0:
            total_completed = -1
            break
        logger.info(f'Retrying metamaplite by dropping failed file.')
        logger.info(f'Looking for completed/failed files to remove from next run.')
        filelist_version += 1
        with open(f'{filename}', encoding='utf8') as fh, \
                open(error_path, 'a', encoding='utf8') as err, \
                open(f'{orig_filename}_{filelist_version}', 'w', encoding='utf8') as out:
            missing_count = 0
            still_todo = 0
            for file in fh.read().split('\n'):
                outfile = Path(f'{file}.files')
                if outfile.exists():
                    total_completed += 1
                    continue
                elif missing_count == 0:  # first record assumed to be faulty
                    logger.info(f'Failed file is likely: {file}. '
                                f'Metamaplite has difficulty with control (and other) characters. '
                                f'You can retry MML on just that file.')
                    err.write(f'{file}\n')
                else:
                    still_todo += 1
                    out.write(f'{file}\n')
                missing_count += 1
        if still_todo == 0:
            break
        logger.info(f'Ready to re-run metamaplite: Remaining: {still_todo}')
        filename = f'{orig_filename}_{filelist_version}'
        logger.info(f'Completed: {total_completed}')
        if filelist_version > max_retry:
            logger.error(f'Too many retries: {max_retry}; exiting process.')
    if total_completed == -1:
        logger.info(f'Completed all.')
    else:
        logger.info(f'Completed all: {total_completed}')
    return res
