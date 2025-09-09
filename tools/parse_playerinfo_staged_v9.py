#!/usr/bin/env python3
import argparse, json, gzip, struct, os, sys
from typing import Dict

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
        for k, v in raw_data.items():
            key = k.lower()
            if key in ("coins", "gold", "xp"):
                result["currencies"][k] = v
            elif key in ("towerlevel", "towerhealth"):
                result["towers"][k] = v
            elif "card" in key:
                result["cards"][k] = v
            elif "module" in key:
                result["modules"][k] = v
            elif "lab" in key:
                result["labs"][k] = v
            elif "relic" in key:
                result["relics"][k] = v
            elif "research" in key:
                result["research"][k] = v
            elif "workshop" in key:
                result["workshop_upgrades"][k] = v
            else:
                result["_raw"][k] = v
    elif isinstance(raw_data, dict) and raw_data.get("__binary__"):
        result["_raw"].update(raw_data)
    else:
        if isinstance(raw_data, dict):
            result["_raw"].update(raw_data)
    return result

def parse_binaryformatter(data: bytes) -> Dict:
    offset = 0
    result = {"__binary__": True, "records": [], "strings": {}, "objects": []}
    string_table = {}
    max_records = 10000
    record_count = 0

    while offset < len(data) and record_count < max_records:
        rec_type = data[offset]
        offset += 1
        record_count += 1

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

        elif rec_type == 9 and offset < len(data):  # PrimitiveType
            prim_type = data[offset]; offset += 1
            if prim_type == 8 and offset + 4 <= len(data):  # Int32
                val = struct.unpack_from("<i", data, offset)[0]; offset += 4
                result["records"].append({"type": "Int32", "value": val})
            elif prim_type == 1 and offset < len(data):  # Bool
                val = bool(data[offset]); offset += 1
                result["records"].append({"type": "Bool", "value": val})
            else:
                result["records"].append({"type": f"Primitive({prim_type})"})
        
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

        elif rec_type in (13, 14) and offset + 4 <= len(data):  # MemberReference types
            ref_id = struct.unpack_from("<i", data, offset)[0]
            offset += 4
            ref_name = string_table.get(ref_id, f"ref_{ref_id}")
            result["records"].append({"type": "MemberReference", "ref_id": ref_id, "ref_name": ref_name})

        else:
            result["records"].append({"type": f"unknown({rec_type})", "at": offset})
            # advance one byte to avoid infinite loop
            offset += 1

    return result

def count_schema_fields(result: Dict) -> Dict[str, int]:
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
    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with ObjectWithMap + MemberReference decoding (staged v9)")
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

    counts = count_schema_fields(result)
    print("Parsing complete.")
    for bucket in ["currencies","towers","cards","modules","labs","relics","research","workshop_upgrades"]:
        print(f"✔ {bucket}: {counts[bucket]} fields mapped")
    print(f"❌ {counts['_raw']} fields left in _raw (see {raw_path})")

if __name__ == "__main__":
    sys.exit(main())
