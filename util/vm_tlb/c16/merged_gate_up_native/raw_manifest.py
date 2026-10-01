#!/usr/bin/env python3
import argparse
import hashlib
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


p = argparse.ArgumentParser()
p.add_argument("directory", type=Path)
p.add_argument("--verify", action="store_true")
a = p.parse_args()
manifest = a.directory / "RAW_SHA256SUMS"
if a.verify:
    lines = manifest.read_text().splitlines()
    for line in lines:
        expected, relative = line.split("  ", 1)
        path = a.directory / relative
        if not path.is_file() or sha(path) != expected:
            raise SystemExit(f"mismatch: {relative}")
    print(f"PASS entries={len(lines)} manifest_sha256={sha(manifest)}")
else:
    files = sorted(x for x in a.directory.rglob("*") if x.is_file() and x.name != "RAW_SHA256SUMS")
    manifest.write_text("".join(f"{sha(x)}  {x.relative_to(a.directory).as_posix()}\n" for x in files))
    print(f"PASS entries={len(files)} manifest_sha256={sha(manifest)}")
