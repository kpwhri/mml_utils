import json
import pathlib
import re
import subprocess
from tempfile import TemporaryDirectory

import click


def run_mml_from_text(text, mml_home, *, restrict_to_sts=None, restrict_to_src=None, output_format='json'):
    restrict_to_sts = f"--restrict_to_sts={','.join(restrict_to_sts)}" if restrict_to_sts else ''
    restrict_to_src = f"--restrict_to_sources={','.join(restrict_to_src)}" if restrict_to_src else ''
    with TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        filepath = temp_path / 'temptext'
        outpath = temp_path / f'temptext.{output_format}'
        with open(filepath, 'w', encoding='utf8') as out:
            out.write(text)
        cmd = (f'metamaplite.bat --outputformat={output_format}'
               f' --overwrite --usecontext {restrict_to_sts} {restrict_to_src}'
               f' --filelist={filepath}'
               f''.split()
               )
        res = subprocess.run(cmd, shell=True, universal_newlines=True, cwd=mml_home)
        with open(outpath, encoding='utf8') as fh:
            data = json.load(fh)
    return data


def update(command, curr):
    if command == '--':
        return []
    elif command.startswith('-'):
        parts = set(re.split(r'\|,', command[1:]))
        return [x for x in curr if x not in parts]
    elif command.startswith('+'):
        parts = re.split(r'\|,', command[1:])
        return curr + parts
    else:
        print(f'Unrecognized command sequence: {command}')
        return curr


def help(sources, semantic_types):
    print('Add sources: +src+MDR|SNOMEDCT_US (https://www.nlm.nih.gov/research/umls/sourcereleasedocs/index.html)')
    print(
        'Add semantic types: +sts+sosy|fndg (https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/SemanticTypes_2018AB.txt)'
    )
    print('Remove all sources: +src--')
    print('Remove all semantic types: +sts--')
    print(f'Current sources: {", ".join(sources)}')
    print(f'Current semantic types: {", ".join(semantic_types)}')
    print(f'To include multiple lines, first line and last line should be `===`.')
    print(f'Type `help` to see this message again.')


@click.command()
@click.argument('mml-home', type=click.Path(exists=True, path_type=pathlib.Path))
def interactive_mml(mml_home: pathlib.Path):
    sources = []
    semantic_types = []
    help(sources, semantic_types)
    while True:
        data = []
        opened = False
        while True:
            datum = input('>> ')
            if datum.strip() == '===':
                if opened:
                    break
                opened = True
            elif datum == 'help':
                help(sources, semantic_types)
            elif datum in {'quit', 'exit', 'q'}:
                return
            elif datum.startswith('+src'):
                sources = update(datum[4:], sources)
                print(f'Current sources: {", ".join(sources)}')
            elif datum.startswith('+sts'):
                semantic_types = update(datum[4:], semantic_types)
                print(f'Current semantic types: {", ".join(semantic_types)}')
            elif not opened:
                data.append(datum)
                break
            else:
                data.append(datum)
        text = '\n'.join(data)
        result = run_mml_from_text(text, mml_home, restrict_to_src=sources, restrict_to_sts=semantic_types)
        print(' === === === ')
        print(f'RESULTS: {len(result)}')
        print(json.dumps(result, indent=2))
        print(' === === === ')


if __name__ == '__main__':
    interactive_mml()
