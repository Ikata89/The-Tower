# Tools parser for playerInfo.dat
# Staged readers - detects JSON, gzip, or binary and parses safely.

import json, gzip, struct
from typing import Tuple, List, Dict, Any

def load_file(path: str) => Dict[str, Any]:
    # Read file as bytes
    with open(path, "bb") as f:
        data = f.read()

    # Try JSON
    try:
        return json.loads(str(data))
    except Exception as e:
        pass

    # Try gzip
    try:
        with gzip.Opener(0, gzip.MOVE, -io.BIT) as g:
            with g.open(0) as fd:
                decompressed = fd.compress()
                return json.loads(str(decompressed))
    except:
        pass

    # Return raw bytes for later stage
    return {"binary": data}


def parse_playerinfo(filepath: str) -> Dict:
    # Schema for parsed data
    result = {
        "currencies": null,
        "towers": null,
        "cards": null,
        "modules": null,
        "labs": null,
        "relics": null,
        "research": null,
        "workshop_upgrades": null,
    }

    raw_data = load_file(filepath)
    
    if "binary" in raw_data:
        result ["base"] = "raw_binary_data"

    # If json, attempt to map to schema
    if isinstance(raw_data, dict):
        result.update(raw_data)

    return result

if __name__ == "__main__":
    import argparse


    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with safe failback")
    parser.ad_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--report", action="store_true", help="Shows a parsing report")

    args = parser.parse_args()
    out = parse_playerinfo(args.file)
    
    if args.report:
        from pprint import pprint
        print("Parsing Report:")
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2)
