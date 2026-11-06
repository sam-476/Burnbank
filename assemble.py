"""Add classes.dex to the aapt2 output and write a 4-byte-aligned APK (what zipalign does)."""
import struct, sys, zipfile

base, dex, out = sys.argv[1], sys.argv[2], sys.argv[3]

entries = []
with zipfile.ZipFile(base) as z:
    for info in z.infolist():
        entries.append((info.filename, z.read(info.filename), info.compress_type))
with open(dex, "rb") as f:
    entries.append(("classes.dex", f.read(), zipfile.ZIP_DEFLATED))

# order: manifest + resources first, then dex, then the rest
def rank(e):
    n = e[0]
    return 0 if n == "AndroidManifest.xml" else 1 if n == "resources.arsc" else 2 if n == "classes.dex" else 3
entries.sort(key=rank)

with zipfile.ZipFile(out, "w") as z:
    offset = 0
    for name, data, ctype in entries:
        # resources.arsc must be stored and aligned (Android 11+); align every stored entry to 4 bytes
        if name == "resources.arsc" or name.startswith("assets/") and name.endswith((".png", ".jpg")):
            ctype = zipfile.ZIP_STORED
        zi = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = ctype
        zi.create_system = 0
        if ctype == zipfile.ZIP_STORED:
            header = 30 + len(name.encode("utf-8"))
            pad = (-(offset + header)) % 4
            if pad:
                # extra field: id 0xd935 (zipalign's padding id), length pad-4 (needs >= 4 bytes)
                if pad < 4: pad += 4
                zi.extra = struct.pack("<HH", 0xD935, pad - 4) + b"\0" * (pad - 4)
        z.writestr(zi, data)
        # compute next offset from the written local header
        offset = z.fp.tell()

# verify alignment of stored entries
with zipfile.ZipFile(out) as z:
    for info in z.infolist():
        if info.compress_type == zipfile.ZIP_STORED:
            data_off = info.header_offset + 30 + len(info.filename.encode("utf-8")) + len(info.extra)
            assert data_off % 4 == 0, (info.filename, data_off)
print("assembled", out, "entries:", len(entries))
