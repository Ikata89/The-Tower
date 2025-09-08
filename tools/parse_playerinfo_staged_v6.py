#!/usr/bin/env python3
import argparse, json, gzip, struct, os, sys
from typing import Dict
from pprint import pprint

def load_file(path: str):
    with open(path, "rb") as f:
        data = f.read()
    try:
        return json.loads(data.decode("utf-8")), "json"
    except Exception:
        pass
    try:
        decompressed = gzip.decompress(data)
        return json.loads(decompressed.decode("utf-8")), "gzip_json"
    except Exception:
        pass
    try:
        return parse_binaryformatter(data), "binaryformatter"
    except Exception:
        return {"_note": "unknown format", "bytes": len(data)}, "unknown"

def parse_playerinfo(filepath: str) -> Dict:
    raw_data, method = load_file(filepath)
    result = {
        "currencies": {},
        "towers": {},
        "_raw": {},
        "_meta": {"method": method},
    }
    if isinstance(raw_data, dict):
        # JSON/gzip case
        for k, v in raw_data.items():
            if k in ("coins", "gold", "xp"):
                result["currencies"][k] = v
            elif k in ("towerLevel", "towerHealth"):
                result["towers"][k] = v
            else:
                result["_raw"][k] = v
    elif isinstance(raw_data, dict) and raw_data.get("__binary__"):
        result["_raw"].update(raw_data)
    else:
        if isinstance(raw_data, dict):
            result["_raw"].update(raw_data)
    return result

# --- BinaryFormatter staged parser ---
def parse_binaryformatter(data: bytes) -> Dict:
    offset = 0
    result = {"__binary__": True, "records": [], "strings": {}}
    string_table = {}
    while offset < len(data):
        rec_type = data[offset]
        offset += 1
        if rec_type == 0:
            if offset + 16 <= len(data):
                root_id, header_id, major, minor = struct.unpack_from("<iiii", data, offset)
                result["records"].append({"type": "StreamHeader", "root": root_id, "header": header_id, "version": f"{major}.{minor}"})
                offset += 16
        elif rec_type == 6:
            if offset + 8 <= len(data):
                obj_id, strlen = struct.unpack_from("<ii", data, offset)
                offset += 8
                if offset + strlen <= len(data):
                    s = data[offset:offset+strlen].decode("utf-8", errors="ignore")
                    offset += strlen
                    string_table[obj_id] = s
                    result["strings"][obj_id] = s
                    result["records"].append({"type": "String", "id": obj_id, "value": s})
        elif rec_type == 9:
            if offset < len(data):
                prim_type = data[offset]
                offset += 1
                if prim_type == 8 and offset + 4 <= len(data):
                    val = struct.unpack_from("<i", data, offset)[0]
                    offset += 4
                    result["records"].append({"type": "Int32", "value": val})
                elif prim_type == 1:
                    val = bool(data[offset])
                    offset += 1
                    result["records"].append({"type": "Bool", "value": val})
                else:
                    result["records"].append({"type": f"Primitive({prim_type})"})
            else:
                break
        else:
            result["records"].append({"type": f"unknown({rec_type})"})
            break
    return result

def count_schema_fields(result: Dict) -> Dict[str, int]:
    return {
        "currencies": len(result.get("currencies", {})),
        "towers": len(result.get("towers", {})),
        "_raw": len(result.get("_raw", {})),
    }

def main():
    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with BinaryFormatter decoding (staged v6)")
    parser.add_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--out", default="out", help="Output folder")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    result = parse_playerinfo(args.file)

    # Write structured schema
    schema_path = os.path.join(args.out, "playerInfo.json")
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Write raw dump
    raw_path = os.path.join(args.out, "playerInfo_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(result.get("_raw", {}), f, indent=2, ensure_ascii=False)

    # Print summary
    counts = count_schema_fields(result)
    print("Parsing complete.")
    print(f"✔ currencies: {counts['currencies']} fields mapped")
    print(f"✔ towers: {counts['towers']} fields mapped")
    print(f"❌ {counts['_raw']} fields left in _raw (see {raw_path})")

if __name__ == "__main__":
    sys.exit(main())
