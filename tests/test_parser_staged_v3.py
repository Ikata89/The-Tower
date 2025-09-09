import json, gzip, io, pytest
from tools.parse_playerinfo_staged_v3 import parse_playerinfo

def test_schema_keys():
    result = parse_playerinfo(".notexist")
    for key in ["currencies", "towers", "cards", "modules", "labs", "relics", "research", "workshop_upgrades"]:
        assert key in result


def test_full_json_parsing(tmp_path):
    data = {
        "currencies": {"coins": 500, "gems": 10, "shards": 3},
        "towers": {"list": [{"name": "BasicTower", "level": 2, "damage": 50}]},
        "cards": {"list": [{"name": "AttackCard", "level": 1, "bonus": 5}]},
        "modules": {"list": [{"name": "DamageModule", "level": 3, "bonus": 15}]},
        "labs": {"list": [{"name": "LabA", "level": 4}]},
        "relics": {"list": [{"name": "RelicX", "level": 1, "effect": "boost"}]},
        "research": {"list": [{"name": "Tech1", "progress": 42}]},
        "workshop_upgrades": {"list": [{"name": "Upgrade1", "level": 7}]}
    }
    file = tmp_path / "save.json"
    file.write_text(json.dumps(data))
    result = parse_playerinfo(str(file))
    
    assert result["currencies"]["coins"] == 500
    assert result["currencies"]["gems"] == 10
    assert result["currencies"]["shards"] == 3

    assert "BasicTower" in result["towers"]
    assert result["towers"]["BasicTower"]["level"] == 2
    assert result["towers"]["BasicTower"]["damage"] == 50

    assert "AttackCard" in result["cards"]
    assert result["cards"]["AttackCard"]["bonus"] == 5

    assert "DamageModule" in result["modules"]
    assert result["modules"]["DamageModule"]["level"] == 3

    assert "LabA" in result["labs"]
    assert result["labs"]["LabA"]["level"] == 4

    assert "RelicX" in result["relics"]
    assert result["relics"]["RelicX"]["effect"] == "boost"

    assert "Tech1" in result["research"]
    assert result["research"]["Tech1"]["progress"] == 42

    assert "Upgrade1" in result["workshop_upgrades"]
    assert result["workshop_upgrades"]["Upgrade1"]["level"] == 7

def test_binary_fallback(tmp_path):
    file = tmp_path / "bin.dat"
    file.write_bytes(b'randombytes')
    result = parse_playerinfo(str(file))
    assert isinstance(result, dict)
