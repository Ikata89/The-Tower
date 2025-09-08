#!/usr/bin/env python3
import argparse, json, os, sys, gzip

def sniff_and_load(raw: bytes):
    # 1) Try plain JSON
    try:
        return json.loads(raw.decode("utf-8")), "json"
    except Exception:
        pass
    # 2) Try gzipped JSON
    try:
        decomp = gzip.decompress(raw)
        return json.loads(decomp.decode("utf-8")), "gzip_json"
    except Exception:
        pass
    # 3) Fallback: expose hex length only (placeholder)
    return {"_note": "unrecognised format", "bytes": len(raw)}, "unknown"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to playerInfo.dat")
    ap.add_argument("--out", default="out", help="Output folder")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    with open(args.input, "rb") as f:
        raw = f.read()

    data, method = sniff_and_load(raw)

    # Emit JSON
    with open(os.path.join(args.out, "playerInfo.json"), "w", encoding="utf-8") as f:
        json.dump({"_method": method, "data": data}, f, ensure_ascii=False, indent=2)

    # Emit CSV (very basic key/value flatten)
    try:
        import csv
        flat = []
        def walk(prefix, obj):
            if isinstance(obj, dict):
                for k,v in obj.items():
                    walk(f"{prefix}.{k}" if prefix else k, v)
            elif isinstance(obj, list):
                for i,v in enumerate(obj):
                    walk(f"{prefix}[{i}]", v)
            else:
                flat.append((prefix, obj))
        walk("", data)
        with open(os.path.join(args.out, "playerInfo.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["key","value"]); w.writerows(flat)
    except Exception:
        pass

    print(f"Parsed with method: {method}. Outputs in {args.out}")

if __name__ == "__main__":
    sys.exit(main())
