import os, json, gzip, subprocess, sys, tempfile
import pytest

from tools import parse_playerinfo_staged_v6 as parser

def make_json_file(tmp_path):
    path = tmp_path / "test.json"
    data = {"gold": 100, "towerLevel": 5, "other": "abc"}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path

def make_gzip_json_file(tmp_path):
    path = tmp_path / "test_gzip.dat"
    data = {"xp": 200}
    raw = json.dumps(data).encode("utf-8")
    compressed = gzip.compress(raw)
    path.write_bytes(compressed)
    return path

def make_bin_file(tmp_path):
    path = tmp_path / "test_bin.dat"
    header = bytes([0]) + (1).to_bytes(4, "little") + (2).to_bytes(4, "little") + (1).to_bytes(4, "little") + (0).to_bytes(4, "little")
    int_record = bytes([9, 8]) + (42).to_bytes(4, "little")
    path.write_bytes(header + int_record)
    return path

def test_parse_json(tmp_path):
    path = make_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["gold"] == 100
    assert result["towers"]["towerLevel"] == 5
    assert "other" in result["_raw"]

def test_parse_gzip_json(tmp_path):
    path = make_gzip_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["xp"] == 200

def test_parse_binary(tmp_path):
    path = make_bin_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["_meta"]["method"] == "binaryformatter"
    assert any(r.get("type") == "Int32" and r.get("value") == 42 for r in result.get("_raw", {}).get("records", []))

def test_cli_report_creates_files(tmp_path):
    path = make_json_file(tmp_path)
    out_dir = tmp_path / "out"
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([sys.executable, "-m", "tools.parse_playerinfo_staged_v6", str(path), "--out", str(out_dir)], check=True)
    schema_file = out_dir / "playerInfo.json"
    raw_file = out_dir / "playerInfo_raw.json"
    assert schema_file.exists()
    assert raw_file.exists()
    data = json.loads(schema_file.read_text(encoding="utf-8"))
    assert "currencies" in data
    raw = json.loads(raw_file.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
