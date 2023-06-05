import json
import tomllib


def parse_config(config_file):
    with open(config_file, 'rb') as fh:
        if config_file.suffix == '.json':
            return json.load(fh)
        elif config_file.suffix == '.toml':
            return tomllib.load(fh)
        else:
            raise ValueError(f'Unrecognized config format: {config_file.suffix} for file: {config_file}.')
