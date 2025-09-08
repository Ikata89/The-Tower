import os, json, gzip, subprocess, sys, pytest
from tools import parse_playerinfo_staged_v8 as parser

def make_json_file(tmp_path):
    path = tmp_path / "test.json"
    data = {"gold": 123, "towerLevel": 4, "cardAttack": 10, "moduleSpeed": 2}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path

def make_gzip_json_file(tmp_path):
    path = tmp_path / "test_gzip.dat"
    data = {"xp": 321}
    raw = json.dumps(data).encode("utf-8")
    compressed = gzip.compress(raw)
    path.write_bytes(compressed)
    return path

def test_parse_json(tmp_path):
    path = make_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["gold"] == 123
    assert result["towers"]["towerLevel"] == 4
    assert "cardAttack" in result["cards"]
    assert "moduleSpeed" in result["modules"]

def test_parse_gzip_json(tmp_path):
    path = make_gzip_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["xp"] == 321

def test_cli_report_creates_files(tmp_path):
    path = make_json_file(tmp_path)
    out_dir = tmp_path / "out"
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([sys.executable, "-m", "tools.parse_playerinfo_staged_v8", str(path), "--out", str(out_dir)], check=True)
    schema_file = out_dir / "playerInfo.json"
    raw_file = out_dir / "playerInfo_raw.json"
    assert schema_file.exists()
    assert raw_file.exists()
    data = json.loads(schema_file.read_text(encoding="utf-8"))
    counts = parser.count_schema_fields(data)
    assert counts["currencies"] >= 1
