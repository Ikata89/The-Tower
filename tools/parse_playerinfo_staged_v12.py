#!/usr/bin/env python3
import argparse, json, gzip, os, sys

def load_file(path: str):
    with open(path, "rb") as f:
        data = f.read()
    try:
        return json.loads(data.decode("utf-8")), "json"
    except Exception:
        pass
    try:
        import gzip as gz
        decompressed = gz.decompress(data)
        return json.loads(decompressed.decode("utf-8")), "gzip_json"
    except Exception:
        pass
    try:
        return parse_binaryformatter(data), "binaryformatter_v12"
    except Exception:
        return {"_note": "unknown format", "bytes": len(data)}, "unknown"

def parse_playerinfo(filepath: str):
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
        "_raw": {},
        "_meta": {"method": method},
    }
    if isinstance(raw_data, dict):
        result["_raw"].update(raw_data)
    return result

def parse_binaryformatter(data: bytes):
    offset = 0
    result = {"__binary__": True, "records": [], "record_summary": {}, "offset_last": 0}
    max_records = 50
    record_count = 0

    while offset < len(data) and record_count < max_records:
        rec_type = data[offset]
        offset += 1
        record_count += 1

        result["record_summary"][rec_type] = result["record_summary"].get(rec_type, 0) + 1
        result["records"].append({"type": rec_type, "offset": offset})

        # Always advance at least 4 bytes to avoid loops
        offset += 4
        result["offset_last"] = offset

    return result

def count_schema_fields(result):
    return {
        "currencies": len(result.get("currencies", {})),
        "towers": len(result.get("towers", {})),
        "cards": len(result.get("cards", {})),
        "modules": len(result.get("modules", {})),
        "labs": len(result.get("labs", {})),
        "relics": len(result.get("relics", {})),
        "research": len(result.get("research", {})),
        "workshop_upgrades": len(result.get("workshop_upgrades", {})),
        "_raw": len(result.get("_raw", {})),
    }

def main():
    parser = argparse.ArgumentParser(description="Strict diagnostic parser for playerInfo.dat (staged v12)")
    parser.add_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--out", default="out", help="Output folder")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    result = parse_playerinfo(args.file)

    schema_path = os.path.join(args.out, "playerInfo.json")
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    raw_path = os.path.join(args.out, "playerInfo_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(result.get("_raw", {}), f, indent=2, ensure_ascii=False)

    if "records" in result.get("_raw", {}):
        print("Parsing complete (diagnostic v12). Record trace:")
        for rec in result["_raw"]["records"]:
            print(f"  type {rec['type']} @ {rec['offset']}")

if __name__ == "__main__":
    sys.exit(main())
