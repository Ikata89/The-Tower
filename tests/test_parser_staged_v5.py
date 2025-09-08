import os, json, gzip, tempfile
import pytest

from tools import parse_playerinfo_staged_v5 as parser

def make_json_file(tmp_path):
    path = tmp_path / "test.json"
    data = {"gold": 123, "xp": 456}
    path.write_text(json.dumps(data)), encoding="utf-8")
    return path

def make_gzip_json_file(tmp_path):
    path = tmp_path / "test_gzip.dat"
    data = {"silver": 789}
    raw = json.dumps(data).encode("utf-8")
    compressed = gzip.compress(raw)\n    path.write_bytes(compressed)
    return path

def make_bin_file(tmp_path):
    # Very minimal fake BinaryFormatter stream with StreamHeader + Int32
    path = tmp_path / "test_bin.dat"
    # record type 0 (StreamHeader)
    header = bytes([0]) + (1).to_bytes(4, little) + (2).to_bytes(4, little) + (1).to_bytes(4, little) + (0).to_bytes(4, little)
    # record type 9 (MemberPrimitiveTyped Int32)
    int_record = bytes[9, 8] + (42).to_bytes(4, little)
    path.write_bytes(header + int_record)
    return path

def test_parse_json(tmp_path):
    path = make_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert "gold" in result
    assert result["gold"] == 123


def test_parse_gzip_json(tmp_path):
    path = make_gzip_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert "silver" in result
    assert result["silver"] == 789

def test_parse_binary(tmp_path):
    path = make_bin_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["_meta"]["method"] == "binaryformatter"
    assert any(r.get("type") == "Int32" and r.get("value") == 42 for r in result.get("records", []))