#!/usr/bin/env python3
import argparse, json, gzip, struct, os, sys
from typing import Dict, Any

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
        return parse_binaryformatter(data), "binaryformatter_diagnostic"
    except Exception:
        return {"_note": "unknown format", "bytes": len(data)}, "unknown"

def parse_playerinfo(filepath: str) -> Dict[str, Any]:
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
    if isinstance(raw_data, dict) and raw_data.get("__binary__"):
        result["_raw"].update(raw_data)
    elif isinstance(raw_data, dict):
        result["_raw"].update(raw_data)
    return result

def parse_binaryformatter(data: bytes) -> Dict[str, Any]:
    offset = 0
    result = {"__binary__": True, "records": [], "record_summary": {}}
    max_records = 100
    record_count = 0

    while offset < len(data) and record_count < max_records:
        rec_type = data[offset]
        offset += 1
        record_count += 1

        # Count the record type
        result["record_summary"][rec_type] = result["record_summary"].get(rec_type, 0) + 1

        # Record basic info
        result["records"].append({"type": rec_type, "offset": offset})

        # Try to skip minimal known structures, else just advance 1 byte
        if rec_type == 0 and offset + 16 <= len(data):  # StreamHeader
            offset += 16
        elif rec_type == 6 and offset + 8 <= len(data):  # String header (skip id+len, but not content)
            offset += 8
        elif rec_type == 12 and offset + 12 <= len(data):  # ObjectWithMap header only
            offset += 12
        elif rec_type in (13, 14) and offset + 4 <= len(data):  # MemberReference
            offset += 4
        else:
            offset += 1  # Always advance

    return result

def count_schema_fields(result: Dict[str, Any]) -> Dict[str, int]:
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
    parser = argparse.ArgumentParser(description="Diagnostic parser for playerInfo.dat (staged v10)")
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

    if "record_summary" in result.get("_raw", {}):
        print("Parsing complete (diagnostic mode). Record counts:")
        for rtype, count in result["_raw"]["record_summary"].items():
            print(f"  type {rtype}: {count}")

if __name__ == "__main__":
    sys.exit(main())
