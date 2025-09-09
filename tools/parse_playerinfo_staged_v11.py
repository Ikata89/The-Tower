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
        return parse_binaryformatter(data), "binaryformatter_v11"
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
    result = {"__binary__": True, "records": [], "strings": {}, "objects": [], "record_summary": {}}
    string_table = {}
    max_records = 500
    record_count = 0

    while offset < len(data) and record_count < max_records:
        rec_type = data[offset]
        offset += 1
        record_count += 1

        result["record_summary"][rec_type] = result["record_summary"].get(rec_type, 0) + 1

        if rec_type == 0 and offset + 16 <= len(data):  # StreamHeader
            root_id, header_id, major, minor = struct.unpack_from("<iiii", data, offset)
            result["records"].append({"type": "StreamHeader", "root": root_id, "header": header_id, "version": f"{major}.{minor}"})
            offset += 16

        elif rec_type == 6 and offset + 8 <= len(data):  # String record
            obj_id, strlen = struct.unpack_from("<ii", data, offset)
            offset += 8
            if offset + strlen <= len(data):
                s = data[offset:offset+strlen].decode("utf-8", errors="ignore")
                offset += strlen
                string_table[obj_id] = s
                result["strings"][obj_id] = s
                result["records"].append({"type": "String", "id": obj_id, "value": s})

        elif rec_type == 12 and offset + 12 <= len(data):  # ObjectWithMap
            obj_id, name_id, field_count = struct.unpack_from("<iii", data, offset)
            offset += 12
            fields = []
            for i in range(field_count):
                if offset + 4 <= len(data):
                    fid = struct.unpack_from("<i", data, offset)[0]
                    offset += 4
                    fields.append(string_table.get(fid, f"field_{fid}"))
            obj_name = string_table.get(name_id, f"class_{name_id}")
            obj = {"id": obj_id, "name": obj_name, "fields": fields}
            result["objects"].append(obj)
            result["records"].append({"type": "ObjectWithMap", "object": obj})

        elif rec_type in (13, 14) and offset + 4 <= len(data):  # MemberReference
            ref_id = struct.unpack_from("<i", data, offset)[0]
            offset += 4
            ref_name = string_table.get(ref_id, f"ref_{ref_id}")
            result["records"].append({"type": "MemberReference", "ref_id": ref_id, "ref_name": ref_name})

        elif 97 <= rec_type <= 122:  # ASCII lowercase letters
            result["records"].append({"type": "AsciiChar", "char": chr(rec_type)})
            # already advanced 1

        elif 65 <= rec_type <= 90:  # ASCII uppercase letters
            result["records"].append({"type": "AsciiChar", "char": chr(rec_type)})
            # already advanced 1

        else:
            result["records"].append({"type": f"unknown({rec_type})", "at": offset})
            offset += 1

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
    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with extended BinaryFormatter decoding (staged v11)")
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
        print("Parsing complete (v11). Record counts:")
        for rtype, count in result["_raw"]["record_summary"].items():
            print(f"  type {rtype}: {count}")

if __name__ == "__main__":
    sys.exit(main())
