import os, json, gzip, subprocess, sys, pytest
from tools import parse_playerinfo_staged_v9 as parser

def make_json_file(tmp_path):
    path = tmp_path / "test.json"
    data = {"gold": 500, "towerHealth": 250, "cardSpeed": 1, "moduleDamage": 2}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path

def make_gzip_json_file(tmp_path):
    path = tmp_path / "test_gzip.dat"
    data = {"xp": 777}
    raw = json.dumps(data).encode("utf-8")
    compressed = gzip.compress(raw)
    path.write_bytes(compressed)
    return path

def test_parse_json(tmp_path):
    path = make_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["gold"] == 500
    assert result["towers"]["towerHealth"] == 250
    assert "cardSpeed" in result["cards"]
    assert "moduleDamage" in result["modules"]

def test_parse_gzip_json(tmp_path):
    path = make_gzip_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["xp"] == 777

def test_cli_report_creates_files(tmp_path):
    path = make_json_file(tmp_path)
    out_dir = tmp_path / "out"
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([sys.executable, "-m", "tools.parse_playerinfo_staged_v9", str(path), "--out", str(out_dir)], check=True)
    schema_file = out_dir / "playerInfo.json"
    raw_file = out_dir / "playerInfo_raw.json"
    assert schema_file.exists()
    assert raw_file.exists()
    data = json.loads(schema_file.read_text(encoding="utf-8"))
    counts = parser.count_schema_fields(data)
    assert counts["currencies"] >= 1
