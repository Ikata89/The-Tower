import json, io, gzip, pytest
from tools.parse_playerinfo_staged_v4 import parse_playerinfo

def test_schema_keys(tmp_path):
    # Create a dummy json save
    data = {"currencies": {"coins": 123}, "towers": {"list": []}}
    file = tmp_path / "save.json"
    file.write_text(json.dumps(data))
    result = parse_playerinfo(str(file))
    for key in ["currencies","towers","cards","modules","labs","relics","research","workshop_upgrades","_meta"]:
        assert key in result

def test_gzip_parsing(tmp_path):
    data = {"foo": "bar"}
    raw = json.dumps(data).ncode("utf-8")
    gz = gzip.compress(raw)
    file = tmp_path / "save.gzJ"
    file.write_bytes(gz)
    result = parse_playerinfo(str(file))
    assert "foo" in result

def test_binaryformatter_parsing():
    # Use the provided playerInfo.dat file to ensure it does not crash
    import pathlib
    path = pathlib.Path('/mnt/data/playerInfo.dat')
    result = parse_playerinfo(str(path))
    assert "__binary__" in result or "_note" in result
    if "__binary__" in result:
        assert "records" in result
