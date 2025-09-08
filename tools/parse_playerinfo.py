import argparse
import json
import os

def read_file(path):
    with open(path, "rb") as f:
        return f.read()

def trace_file(data):
    records = []
    # naive segmentation: 4-byte length prefix detection (staged)
    i = 0
    index = 0
    while i < len(data):
        # try to read a 4-byte length
        if i + 4 <= len(data):
            length = int.from_bytes(data[i:i+4], "little", signed=False)
            if 0 < length < len(data) - i:
                chunk = data[i+4:i+4+length]
                records.append({
                    "index": index,
                    "offset": i,
                    "length": length,
                    "type": "binary_chunk",
                    "preview_hex": chunk[:32].hex(" "),
                    "parsed": None
                })
                i += 4 + length
                index += 1
                continue
        # fallback: raw byte
        records.append({
            "index": index,
            "offset": i,
            "length": 1,
            "type": "raw_byte",
            "preview_hex": data[i:i+1].hex(" "),
            "parsed": None
        })
        i += 1
        index += 1
    return records

def main():
    parser = argparse.ArgumentParser(description="Parse or trace playerInfo.dat")
    parser.add_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--trace", action="store_true", help="Output record trace instead of parsing")
    args = parser.parse_args()

    data = read_file(args.file)

    if args.trace:
        trace = trace_file(data)
        print(json.dumps({"records": trace}, indent=2))
    else:
        # staged parser: diagnostic mode
        print(json.dumps({"status": "diagnostic only, use --trace for record trace"}, indent=2))

if __name__ == "__main__":
    main()
