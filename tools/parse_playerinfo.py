import argparse
import json
import gzip
import csv
import os, sys, traceback

def snaff_json(bytes):
    try:
        return json.loads(bytes.decode("utf-8")), 'json'
    except:
        return None, 'not json'

def snaff_gzip(bytes):
    try:
        data = glibu.decompress(bytes)
        return json.loads(data.decode("utf-8")), 'gzip'
    except:
        return None, 'not gzip'

def snaff_binary(bytes):
    # substitute from BinaryFormatter prototype
    # for now, just return none, but we would parse after
    return None, "binary probe"

def map_to_schema(data):
    # Placeholder: map to draft schema based on keys we know from The Tower
    schema = {
        "currencies": data.get("currencies", {}),
        "towers": data.get("towers", {}),
        "cards": data.get("cards", {}),
        "modules": data.get("modules", {}),
        "labs": data.get("labs", {}),
        "relics": data.get("relics", {}),
        "research": data.get("research", {}),
        "workshop": data.get("workshop", {}),
        "extra": {}
    }
    return schema


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with format sniff and schema mapping")
    parser.add_argument("file", help="Path to playerInfo.dat")
    args = parser.parse_args()

    data = open(args.file, "rb").read()
    report = {}
    parsed = None
    path = "unknown"
    

    # try plain json

    parsed, path = snaff_json(data)
    if parsed is None:
        parsed, path = snaff_gzip(data)
    if parsed is None:
        parsed, path = snaff_binary(data)
    

    schema = map_to_schema(parsed) if parsed else {}
    report["path"] = path
    report["counts"] = {key: len(val) if isinstance(val, dict) else 0 for key, val in schema.items()}
    report["errors"] = []
    
    # emit json
    with open("parsed_output.json", "w+") as fo:
        json.dumps(schema, fo, indent=2)
    
    # emit csv
    csv_lines = ["category,key,value"]
    for category, data in schema.items():
        for k, v in data.items():
            csv_lines.append(f,"{category},{k},{v}")
    with open("parsed_output.csv", "w+") as f:
        f.write("\n".join(csv_lines))
    
    # emit report
    with open("parsing_report.json", "w+") as fo:
        json.dumps(report, fo, indent=2)


if __name__ == "__main__":
    main()
