# Staged parser v5: extends BinaryFormatter parsing with string resolution and primitive extraction.

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
    try:
        return parse_binaryformatter(data), "binaryformatter"
    except Exception as e:
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
        "_meta": {"method": method},
    }
    if isinstance(raw_data, dict):
        result.update(raw_data)
    return result

# --- BinaryFormatter staged reader ---
def parse_binaryformatter(data: bytes) -> Dict:
    offset = 0
    result = {"__binary__": True, "records": [], "strings": {}}
    string_table = {}
    while offset < len(data):
        rec_type = data[offset]
        offset += 1
        if rec_type == 0:  # SerializedStreamHeader
            root_id, header_id, major, minor = struct.unpack_from("<iiii", data, offset)
            result["records"].append({"type": "StreamHeader", "root": root_id, "header": header_id, "version": f"{major}.{minor}"})
            offset += 16
        elif rec_type == 6:  # BinaryObjectString
            obj_id, strlen = struct.unpack_from("<ii", data, offset)
            offset += 8
            s = data[offset:offset+strlen].decode("utf-8", errors="ignore")
            offset += strlen
            string_table[obj_id] = s
            result["strings"][obj_id] = s
            result["records"].append({"type": "String", "id": obj_id, "value": s})
        elif rec_type == 12:  # BinaryObjectWithMap
            obj_id, name_id, field_count = struct.unpack_from("<iii", data, offset)
            offset += 12
            fields = []
            for i in range(field_count):
                if offset+4 <= len(data):
                    str_id = struct.unpack_from("<i", data, offset)[0]
                    offset += 4
                    fields.append(string_table.get(str_id, f"str_{str_id}"))
            result["records"].append({"type": "ObjectWithMap", "obj_id": obj_id, "name": string_table.get(name_id, f"str_{name_id}"), "fields": fields})
        elif rec_type == 9:  # MemberPrimitiveTyped (int32, bool, etc.)
            prim_type = data[offset]; offset += 1
            if prim_type == 8:  # Int32
                val = struct.unpack_from("<i", data, offset)[0]
                offset += 4
                result["records"].append({"type": "Int32", "value": val})
            elif prim_type == 1:  # Boolean
                val = bool(data[offset]); offset += 1
                result["records"].append({"type": "Bool", "value": val})
            else:
                result["records"].append({"type": f"Primitive({prim_type})"})
                offset += 1
        else:
            result["records"].append({"type": f"Unknown({rec_type})"})
            break
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with BinaryFormatter decoding")
    parser.add_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--report", action="store_true", help="Shows a parsing report")
    args = parser.parse_args()
    out = parse_playerinfo(args.file)
    if args.report:
        from pprint import pprint
        pprint(out)
    else:
        print(json.dumps(out, indent=2))
