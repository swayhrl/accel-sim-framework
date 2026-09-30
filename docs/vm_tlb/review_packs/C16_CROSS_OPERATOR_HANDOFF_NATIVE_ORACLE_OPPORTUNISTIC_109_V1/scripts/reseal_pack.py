#!/usr/bin/env python3
"""Generate deterministic SHA256SUMS without touching scientific artifacts."""

import argparse
import hashlib
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pack", type=Path, required=True)
    args = p.parse_args()
    lines = [f"{sha(path)}  {path.relative_to(args.pack)}" for path in sorted(
        x for x in args.pack.rglob("*") if x.is_file() and x.name != "SHA256SUMS" and "__pycache__" not in x.parts)]
    (args.pack / "SHA256SUMS").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
