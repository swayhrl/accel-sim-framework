#!/usr/bin/env python3
"""Verify recovered M5.E1 Rodinia 3.1 input provenance without running CUDA."""

import argparse
import hashlib
import json
from pathlib import Path


ARCHIVE_SHA256 = "b90994d5208ec5a0a133dfb9ab7928a1e8a16741503a91d212884b9e4fce8cd8"
FROZEN_INPUTS = {
    "cfd/fvcorr.domn.097K": "43534e58454ba8baf95253e14d3b07150b9960577e922a954d6e51142a27abfa",
    "b+tree/mil.txt": "1b52b1caf9e0926afbe070cd96327e2645dade902fe9cfd078938ff6d755a29d",
    "b+tree/command.txt": "3c07868498ad4646db842f3c5aeabcde7f3b4e6ebf209578d6b4e690a3d7f8da",
    "dwt2d/192.bmp": "595e63ccd303dcc3387d0fea97d96be524a6f32f5e7593ab09a2704c7571207e",
    "hotspot/temp_512": "503e20bbed397d6799dd55ce928dadc300c0a7834bf7d9ad69eda73c67d23172",
    "hotspot/power_512": "863d922187ae70f8eefda603b71a161a9e61bc4cf7f4cc0cb2c0b8feead58471",
}
GAUSSIAN_CANDIDATES = {
    "gaussian/matrix4.txt": "dda3ac09727d7dc785b9d0bf96d15dcf7afb758fcfba06d539a91304969d587a",
    "gaussian/matrix208.txt": "5da49623c6d7b237a018dc1465b21eb21888564c66a945732235408546c8557a",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(root: Path, expected: dict[str, str]) -> dict[str, str]:
    result = {}
    for relative, known_hash in expected.items():
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"missing required input: {relative}")
        actual = sha256(path)
        if actual != known_hash:
            raise RuntimeError(f"sha256 mismatch: {relative}: {actual}")
        result[relative] = actual
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--include-gaussian-candidates", action="store_true")
    args = parser.parse_args()

    expected = dict(FROZEN_INPUTS)
    if args.include_gaussian_candidates:
        expected.update(GAUSSIAN_CANDIDATES)
    validated = verify(args.root, expected)
    result = {
        "status": "PASS",
        "frozen_input_count": len(FROZEN_INPUTS),
        "gaussian_candidates_checked": args.include_gaussian_candidates,
        "inputs": validated,
        "lud": "SOURCE_GENERATED_-s_256_-v_NO_EXTERNAL_FILE",
    }
    if args.archive is not None:
        actual = sha256(args.archive)
        if actual != ARCHIVE_SHA256:
            raise RuntimeError(f"archive sha256 mismatch: {actual}")
        result["archive_sha256"] = actual
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
