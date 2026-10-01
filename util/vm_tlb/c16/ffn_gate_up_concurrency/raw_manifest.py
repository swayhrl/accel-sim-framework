#!/usr/bin/env python3
"""Create or verify a deterministic SHA256 manifest for a raw directory."""

import argparse
import hashlib
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    manifest = args.directory / "RAW_SHA256SUMS"
    if args.verify:
        failures = []
        for line in manifest.read_text().splitlines():
            digest, relative = line.split("  ", 1)
            path = args.directory / relative
            if not path.is_file() or sha256(path) != digest:
                failures.append(relative)
        if failures:
            raise SystemExit("manifest mismatch: " + ", ".join(failures))
        print(f"PASS entries={len(manifest.read_text().splitlines())} sha256={sha256(manifest)}")
        return
    files = sorted(path for path in args.directory.rglob("*")
                   if path.is_file() and path.name != manifest.name)
    lines = [f"{sha256(path)}  {path.relative_to(args.directory).as_posix()}" for path in files]
    manifest.write_text("\n".join(lines) + "\n")
    print(f"PASS entries={len(lines)} sha256={sha256(manifest)}")


if __name__ == "__main__":
    main()
