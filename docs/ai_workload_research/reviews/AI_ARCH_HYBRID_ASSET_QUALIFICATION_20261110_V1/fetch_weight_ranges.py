#!/usr/bin/env python3
"""Resume two fixed LFS files with checked HTTP ranges; never loads tensors."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import os
from pathlib import Path
import subprocess


ROOT = Path("/data/c16/aiarch_hybrid_asset_qualification_20261110_v1/models/qwen3_5_4b")
BASE = "https://hf-mirror.com/Qwen/Qwen3.5-4B/resolve/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"
FILES = (
    ("model.safetensors-00001-of-00002.safetensors", 5329398688,
     "26a93f066e1916adb13453dae5a0c707c0fbc71299ed98779571a907b8e74c61"),
    ("model.safetensors-00002-of-00002.safetensors", 3990429408,
     "cb544bd9bfae93dc59b0f22b292f5933573854a7f9b97835c67060d7d910e188"),
)
CHUNK_BYTES = 128 * 1024 * 1024
WORKERS = 6


def fetch_chunk(name: str, start: int, end: int) -> Path:
    out = ROOT / f"{name}.range.{start}-{end}"
    expected = end - start + 1
    if out.exists() and out.stat().st_size == expected:
        return out
    tmp = Path(str(out) + ".tmp")
    url = f"{BASE}/{name}"
    command = [
        "curl", "-fL", "-sS", "--connect-timeout", "15", "--max-time", "600",
        "--retry", "2", "--retry-delay", "3", "--speed-time", "60",
        "--speed-limit", "10240", "-r", f"{start}-{end}", "-o", str(tmp),
        "-w", "%{http_code}", url,
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0 or result.stdout.strip() != b"206":
        raise RuntimeError(f"range {name}:{start}-{end}: curl={result.returncode}, HTTP={result.stdout!r}, stderr={result.stderr.decode(errors='replace')}")
    if tmp.stat().st_size != expected:
        raise RuntimeError(f"range {name}:{start}-{end}: got {tmp.stat().st_size}, expected {expected}")
    os.replace(tmp, out)
    return out


def assemble(name: str, total: int, expected_hash: str, parts: list[Path]) -> None:
    prefix = ROOT / f"{name}.part"
    output = ROOT / name
    assembled = ROOT / f"{name}.assembled.part"
    digest = hashlib.sha256()
    with assembled.open("wb") as dst:
        for source in [prefix, *parts]:
            with source.open("rb") as src:
                while block := src.read(4 * 1024 * 1024):
                    digest.update(block)
                    dst.write(block)
    if assembled.stat().st_size != total or digest.hexdigest() != expected_hash:
        raise RuntimeError(f"{name}: final size/hash mismatch: {assembled.stat().st_size}, {digest.hexdigest()}")
    os.chmod(assembled, 0o600)
    os.replace(assembled, output)
    prefix.unlink()
    for part in parts:
        part.unlink()
    print(f"VERIFIED {name} {total} {expected_hash}", flush=True)


def main() -> None:
    planned = []
    jobs = []
    for name, total, expected_hash in FILES:
        output = ROOT / name
        if output.exists() and output.stat().st_size == total:
            with output.open("rb") as src:
                digest = hashlib.file_digest(src, "sha256").hexdigest()
            if digest == expected_hash:
                print(f"ALREADY_VERIFIED {name} {total} {digest}", flush=True)
                continue
        prefix = ROOT / f"{name}.part"
        if not prefix.exists():
            prefix.touch()
        start = prefix.stat().st_size
        if start >= total:
            raise RuntimeError(f"{name}: prefix size {start} is not below expected {total}")
        spans = [(s, min(s + CHUNK_BYTES, total) - 1) for s in range(start, total, CHUNK_BYTES)]
        planned.append((name, total, expected_hash, spans))
        jobs.extend((name, s, e) for s, e in spans)
        print(f"PLAN {name}: prefix={start}, ranges={len(spans)}", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(fetch_chunk, *job) for job in jobs]
        for future in as_completed(futures):
            future.result()
    for name, total, expected_hash, spans in planned:
        parts = [ROOT / f"{name}.range.{s}-{e}" for s, e in spans]
        assemble(name, total, expected_hash, parts)


if __name__ == "__main__":
    main()
