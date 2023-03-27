from mml_utils.parse.json import iter_json_matches_from_file


def test_iter_json_matches_from_file(file0_path):
    target_fields = ['matchedtext', 'start', 'end', 'length']
    for fields in iter_json_matches_from_file(file0_path, *target_fields):
        assert len(fields) == len(target_fields)
        assert isinstance(fields[0], str)
        assert isinstance(fields[1], int)
        assert isinstance(fields[2], int)
        assert isinstance(fields[3], int)
        assert fields[1] + fields[3] == fields[2]
