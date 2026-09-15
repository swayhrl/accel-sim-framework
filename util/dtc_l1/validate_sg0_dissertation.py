#!/usr/bin/env python3
"""Verify direct Chapter-4 evidence without inferring transaction granularity."""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path


PDF_SHA256 = "a9482b420b62636aac379c4a9e670c0f09ec78c287d51fe90a4ac02d66687213"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_text(pdf: Path, page: int) -> str:
    return subprocess.check_output(
        ["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
        text=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    args = parser.parse_args()
    if sha256(args.pdf) != PDF_SHA256:
        raise SystemExit("FAIL dissertation PDF SHA-256 mismatch")
    page_53 = page_text(args.pdf, 71)
    page_61 = page_text(args.pdf, 79)
    for text, anchor in (
        (page_53, "MSHR 的作用是合并相同地址的缺失访存请求"),
        (page_53, "会发出重复的缺失请求"),
        (page_53, "发出重复请求的情况很少"),
        (page_61, "缓存行大小通常为 128 字节"),
    ):
        if re.sub(r"\s+", "", anchor) not in re.sub(r"\s+", "", text):
            raise SystemExit(f"FAIL Chapter-4 anchor missing: {anchor}")
    print("PASS SG0 Chapter-4 direct evidence: duplicate semantics explicit; lower-request granularity unspecified")


if __name__ == "__main__":
    main()
