import os, json, gzip, subprocess, sys, pytest
from tools import parse_playerinfo_staged_v7 as parser

def make_json_file(tmp_path):
    path = tmp_path / "test.json"
    data = {
        "gold": 50,
        "towerLevel": 3,
        "cardAttack": 10,
        "moduleSpeed": 2,
        "labBonus": 5,
        "relicPower": 7,
        "researchPoints": 12,
        "workshopUpgrade": 1,
        "unmappedThing": 999,
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path

def make_gzip_json_file(tmp_path):
    path = tmp_path / "test_gzip.dat"
    data = {"xp": 200}
    raw = json.dumps(data).encode("utf-8")
    compressed = gzip.compress(raw)
    path.write_bytes(compressed)
    return path

def test_parse_json(tmp_path):
    path = make_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["gold"] == 50
    assert result["towers"]["towerLevel"] == 3
    assert "cardAttack" in result["cards"]
    assert "moduleSpeed" in result["modules"]
    assert "labBonus" in result["labs"]
    assert "relicPower" in result["relics"]
    assert "researchPoints" in result["research"]
    assert "workshopUpgrade" in result["workshop_upgrades"]
    assert "unmappedthing" in result["_raw"]

def test_parse_gzip_json(tmp_path):
    path = make_gzip_json_file(tmp_path)
    result = parser.parse_playerinfo(str(path))
    assert result["currencies"]["xp"] == 200

def test_cli_report_creates_files(tmp_path):
    path = make_json_file(tmp_path)
    out_dir = tmp_path / "out"
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([sys.executable, "-m", "tools.parse_playerinfo_staged_v7", str(path), "--out", str(out_dir)], check=True)
    schema_file = out_dir / "playerInfo.json"
    raw_file = out_dir / "playerInfo_raw.json"
    assert schema_file.exists()
    assert raw_file.exists()
    data = json.loads(schema_file.read_text(encoding="utf-8"))
    counts = parser.count_schema_fields(data)
    assert counts["currencies"] >= 1
    assert counts["_raw"] >= 1
