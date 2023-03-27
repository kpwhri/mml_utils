from mml_utils.scripts.run_afep_multi import run_afep_algorithm_multi


def build_toml(outdir, *dirs):
    with open(outdir / 'config.toml', 'w', encoding='utf8') as out:
        out.write(f'outdir = "{outdir.as_posix()}"\n')
        for d in dirs:
            out.write('[[runs]]\n')
            out.write(f'note_directories = ["{d.as_posix()}"]\n')
    return outdir / 'config.toml'


def test_run_afep_multi(tmp_path, fever_dir, short_fever_dir):
    """Ensure that an excel file is created."""
    toml_file = build_toml(tmp_path, fever_dir, short_fever_dir)
    run_afep_algorithm_multi(toml_file)
    assert (tmp_path / 'afep_summary.xlsx').exists()
