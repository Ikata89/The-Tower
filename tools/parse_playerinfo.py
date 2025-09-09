import argparse
import json
import struct

# Map of known BinaryFormatter record type IDs
RECORD_TYPES = {
    0: "SerializedStreamHeader",
    1: "ClassWithId",
    5: "MemberReference",
    6: "BinaryLibrary",
    12: "BinaryObjectString",
    15: "BinaryObjectWithMap",
    16: "ObjectNull",
    17: "MessageEnd",
}

def read_int(buf, i):
    return struct.unpack_from("<i", buf, i)[0], i + 4

def parse_binaryformatter(buf, limit=100):
    records = []
    i = 0
    count = 0

    while i < len(buf) and count < limit:
        rec_type = buf[i]
        rec_name = RECORD_TYPES.get(rec_type, "Unknown")
        record = {"offset": i, "record_type_id": rec_type, "record_type": rec_name}
        i += 1

        try:
            if rec_type == 0:  # SerializedStreamHeader
                root_id, i = read_int(buf, i)
                header_id, i = read_int(buf, i)
                major, i = read_int(buf, i)
                minor, i = read_int(buf, i)
                record.update({
                    "root_id": root_id,
                    "header_id": header_id,
                    "version": f"{major}.{minor}"
                })

            elif rec_type == 6:  # BinaryLibrary
                lib_id, i = read_int(buf, i)
                strlen, i = read_int(buf, i)
                text = buf[i:i+strlen].decode("utf-8", errors="ignore")
                i += strlen
                record.update({"library_id": lib_id, "library_name": text})

            elif rec_type == 12:  # BinaryObjectString
                obj_id, i = read_int(buf, i)
                strlen, i = read_int(buf, i)
                text = buf[i:i+strlen].decode("utf-8", errors="ignore")
                i += strlen
                record.update({"object_id": obj_id, "value": text})

            elif rec_type == 5:  # MemberReference
                id_ref, i = read_int(buf, i)
                record.update({"id_ref": id_ref})

            elif rec_type == 17:  # MessageEnd
                record.update({"info": "End of stream"})
                break

            else:
                # Unknown record, show some hex
                record.update({"preview_hex": buf[i:i+16].hex(" ")})
                i += 1

        except Exception as e:
            record.update({"error": str(e)})
            i += 1

        records.append(record)
        count += 1

    return records

def main():
    parser = argparse.ArgumentParser(description="BinaryFormatter diagnostic parser")
    parser.add_argument("file", help="Path to playerInfo.dat")
    parser.add_argument("--binarytrace", action="store_true", help="Trace BinaryFormatter records")
    args = parser.parse_args()

    data = open(args.file, "rb").read()

    if args.binarytrace:
        trace = parse_binaryformatter(data, limit=200)
        print(json.dumps({"records": trace}, indent=2))
    else:
        print(json.dumps({"status": "use --binarytrace for BinaryFormatter record trace"}, indent=2))

if __name__ == "__main__":
    main()
