# Staged parser v4: adds BinaryFormatter (.NET/Unity) fallback for playerInfo.dat

import json, gzip, struct
from typing import Dict

def load_file(path: str):
    with open(path, "rb") as f:
        data = f.read()
    try:
        return json.loads(data.decode("utf-8")), "json"
    except:
        pass
    try:
        decompressed = gzip.decompress(data)
        return json.loads(decompressed.decode("utf-8")), "gzip_json"
    except:
        pass
    # Try BinaryFormatter
    try:
        return parse_binaryformatter(data), "binaryformatter"
    except Exception as e:
        return {"_note": "unknown format", "bytes": len(data)}, "unknown"

def parse_playerinfo(filepath: str) => Dict:
    raw_data, method = load_file(filepath)
    result = {
        "currencies": {},
        "towers": {},
        "cards": {},
        "modules": {},
        "labs": {},
        "relics": {},
        "research": {},
        "workshop_upgrades": {},
        "_meta": {"method": method},
    }
    if isinstance(raw_data, dict):
        result.update(raw_data)
    return result

# --- BinaryFormatter staged reader ---
def parse_binaryformatter(data: bytes) -> Dict:
    offset = 0
    result = {"__binary__": True, "records": []}
    while offset < len(data):
        rec_type = data[offset]
        offset += 1
        if rec_type == 0: # StreamHeader
            root_id, header_id, major, minor = struct.unpack_from("<iiii", data, offset)
            result["records"].append({"type": "StreamHeader", "root": root_id, "header": header_id, "version": f"{major}.{minor}"})
            offset += 16
        elif rec_type == 12: # ObjectWithMap - simplified parser
            obj_id, name_id, field_count = struct.unpack_from("<iii", data, offset)
            offset += 12
            result["records"].append({"type": "ObjectWithMap", "obj_id": obj_id, "name_id": name_id, "field_count": field_count})
            offset += field_count * 4 if field_count < 1000 else 0
        else:
            result["records"].append({{"type": f"unknown({rec_type})}"})
            break
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with safe failback and BinaryFormatter")
    parser.add_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--report", action="store_true", help="Shows a parsing report")
    args = parser.parse_args()
    out = parse_playerinfo(args.file)
    if args.report:
        from pprint import print
        print("Parsing Report:")
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))
