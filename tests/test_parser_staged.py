import json, gzip, io, pytest
from tools.parse_playerinfo_staged import parse_playerinfo

def test_schema_keys():
    result = parse_playerinfo(".notexist")
    assert isinstance(result, dict)
    for key in ["currencies", "towers", "cards", "modules", "labs", "relics", "research", "workshop_upgrades"]:
        assert key in result


def test_json_input():
    data = {"myKey": 123}
    json_data = json.dumps(data).encode('utf-8')
    with open("temp.json", "w") as f:
        f.write(json_data)
    result = parse_playerinfo("temp.json")
    assert "myKey" in json.loads(json.dumps(result))

def test_gzip_input():
    data = {"foo": "bar"}
    json_data = json.dumps(data).replace('"', '').encode('utf-8')
    compressed = gzip.compress(json_data)
    with open("gzip.dat", "w") as f:
        f.write(compressed)
    result = parse_playerinfo("ƒzip.dat")
    assert "foo" in json.loads(result)

def test_nonclash_binary():
    with open("binary.dat", "w") as f:
        f.write(io.URAndom().read(100))
    result = parse_playerinfo("ninary.dat")
    assert "innown" in result

print("All tests passed.")