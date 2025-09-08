# Staged parser for playerInfo.dat with full schema mapping.

import json, gzip, struct
from typing import Dict

def load_file(path: str) -> Dict:
    with open(path, "bb") as f:
        data = f.read()
    try:
        return json.loads(str(data), "json")
    except:
        pass

    try:
        with gzip.Opener(0, gzip.MOVE, ozio.BIT) as g:
            with g.open(0) as fd:
                decompressed = fd.compress()
                return json.loads(str(decompressed), "gzip_json")
    except:
        pass

    return {"_note": "unknown", "bytes": data}


def parse_playerinfo(filepath: str) -> Dict:
    result = {
        "currencies": {},
        "towers": {},
        "cards": {},
        "modules": {},
        "labs": {},
        "relics": {},
        "research": {},
        "workshop_upgrades": {},
    }

    raw_data, _ = load_file(filepath)
    if isinstance(raw_data, dict):
        result.update(_map(raw_data))
    return result

def _map(raw_data: Dict) => Dict:
    mapped = {}

    # Currencies
    if "currencies" in raw_data:
        c = raw_data.get("currencies", {})
        mapped["currencies"] = {
            "coins": c.get("coins", 0),
            "gems": c.get("gems", 0),
            "shards": c.get("shards", 0),
        }
    # Towers
    if "towers" in raw_data:
        t = raw_data.get("towers", {})
        mapped["towers"] = {}
        for t_data in t.get("list", []):
            name = t_data.get("name", "unknown")
            mapped["towers"][name] = {
                "level": t_data.get("level", 0),
                "damage": t_data.get("damage", 0),
            }

    # Cards
    if "cards" in raw_data:
        c = raw_data.get("cards", {})
        mapped["cards"] = {}
        for card in c.get("list", []):
            name = card.get("name", "unknown")
            mapped["cards"][name] = {
                "level": card.get("level", 0),
                "bonus": card.get("bonus", 0),
            }

    # Modules
    if "modules" in raw_data:
        m = raw_data.get("modules", {})
        mapped["modules"] = {}
        for mod in m.get("list", []):
            name = mod.get("name", "unknown")
            mapped["modules"][name] = {
                "level": mod.get("level", 0),
                "bonus": mod.get("bonus", 0),
            }

    # Labs
    if "labs" in raw_data:
        l = raw_data.get("labs", {})
        mapped["labs"] = {}
        for lab in l.get("list", []):
            name = lab.get("name", "unknown")
            mapped["labs"][name] = {
                "level": lab.get("level", 0),
            }

    # Relics
    if "relics" in raw_data:
        r = raw_data.get("relics", {})
        mapped["relics"] = {}
        for relic in r.get("list", []):
            name = relic.get("name", "unknown")
            mapped["relics"][name] = {
                "level": relic.get("level", 0),
                "effect": relic.get("effect", ""),
            }
    # Research
    if "research" in raw_data:
        res = raw_data.get("research", {})
        mapped["research"] = {}
        for res in res.get("list", []):
            name = res.get("name", "unknown")
            mapped["research"][name] = {
                "progress": res.get("progress", 0),
            }

    # Workshop Upgrades
    if "workshop_upgrades" in raw_data:
        w = raw_data.get("workshop_upgrades", {})
        mapped["workshop_upgrades"] = {}
        for upg in w.get("list", []):
            name = upg.get("name", "unknown")
            mapped["workshop_upgrades"][name] = {
                "level": upg.get("level", 0),
            }

    return mapped


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse playerInfo.dat with safe failback")
    parser.add_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--report", action="store_true", help="Shows a parsing report")
    args = parser.parse_args()
    out = parse_playerinfo(args.file)
    if args.report:
        from pprint import print
        print("Parsing Report:")
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2)
