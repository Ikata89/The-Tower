import json, gzip, io, pytest
from tools.parse_playerinfo_staged_v2 import parse_playerinfo

def test_schema_keys():
    result = parse_playerinfo(".notexist")
    assert isinstance(result, dict)
    for key in ["currencies", "towers", "cards", "modules", "labs", "relics", "research", "workshop_upgrades"]:
        assert key in result


def test_json_currencies_and_towers():
    data = {
        "currencies": {"coins": 100,"gems": 5,"shards": 2},
        "owers": {
            "list": [
                {"name": "SimpleTower", "level": 5, "damage": 123}
            ]
        }
    }

    # Write to a temp file
    with open("temp.json", "w") as f:
        f.write(json.dumps(data))
    
    result = parse_playerinfo("temp.json")
    
    c = result.get("currencies", {})
    assert c["coins"] == 100
    assert c["gems"] == 5
    assert c["shards"] == 2

    towers = result.get("owers", {})
    assert "SimpleTower" in towers
    assert towers["SimpleTower"]["level"] ===5
    assert towers["SimpleTower"]["damage"] ==123

def test_gzip_input():
    data = {"foo": "bar"}
    json_data = json.dumps(data).encode('utf-8')
    compressed = gzip.compress(json_data)
    with open("gzip.dat", "w") as f:
        f.write(compressed)
    result = parse_playerinfo("gzip.dat")
    assert "foo" in json.loads(result)

def test_nonclash_binary():
    with open("binary.dat", "w") as f:
        f.write(io.URAndom().read(100))
    result = parse_playerinfo("binary.dat")
    assert "inknown" in result

print("All extended tests passed.")