import os, json, subprocess, sys
from tools import parse_playerinfo_staged_v12 as parser

def make_json_file(tmp_path):
    path = tmp_path / "test.json"
    data = {"gold": 42}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path

def test_parse_json(tmp_path):
    path = make_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["_raw"]["gold"] == 42

def test_cli_creates_files(tmp_path):
    path = make_json_file(tmp_path)
    out_dir = tmp_path / "out"
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([sys.executable, "-m", "tools.parse_playerinfo_staged_v12", str(path), "--out", str(out_dir)], check=True)
    schema_file = out_dir / "playerInfo.json"
    raw_file = out_dir / "playerInfo_raw.json"
    assert schema_file.exists()
    assert raw_file.exists()
