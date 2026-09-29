#!/usr/bin/env python3
"""Build deterministic review-pack SHA256SUMS without self-reference."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile


PACK = Path(
    "/root/workspace/accel-sim-framework-awma-r101r4-local-service-path-localization-174-v1/"
    "docs/vm_tlb/review_packs/AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    target = PACK / "SHA256SUMS"
    paths = sorted(path for path in PACK.rglob("*")
                   if path.is_file() and not path.is_symlink() and path != target)
    data = "".join(f"{sha256(path)}  {path.relative_to(PACK)}\n" for path in paths).encode()
    fd, temporary = tempfile.mkstemp(prefix=".SHA256SUMS.", dir=PACK)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    print(f"entries={len(paths)} sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
