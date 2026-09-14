#!/usr/bin/env python3
"""Fail-closed C16 U4 importer for a server-transferred exact Llama asset."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

MODEL = "meta-llama/Llama-3.2-1B"
REVISION = "4e20de362430cd3b72f300e6b0f18e50e7166e08"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def payload_manifest(receipt: dict) -> dict:
    entries = receipt.get("payloads", receipt.get("files", []))
    result = {}
    for entry in entries:
        name = entry.get("filename") or Path(str(entry.get("path", ""))).name
        size = entry.get("size", entry.get("size_bytes"))
        sha = entry.get("sha256")
        if name is not None and size is not None and sha:
            result[str(name)] = {"size": int(size), "sha256": str(sha)}
    return result


def validate(incoming: Path, authority: Path, source_receipt: Path | None) -> dict:
    result = {"status": "U4_LOCAL_ASSET_IMPORT_FAIL", "incoming": str(incoming), "errors": []}
    if not incoming.is_dir():
        result["errors"].append("incoming directory is absent")
        return result
    authority_data = json.loads(authority.read_text())
    if authority_data["success_boundary"]["model"] != f"{MODEL}@{REVISION}":
        result["errors"].append("repository authority model/revision drift")
    expected_payloads = {}
    if source_receipt is None:
        result["errors"].append("missing authoritative --source-receipt")
    elif not source_receipt.is_file():
        result["errors"].append("specified source receipt is absent")
    else:
        try:
            p = json.loads(source_receipt.read_text())
            identity = p.get("identity", {})
            source_model = p.get("model_id", p.get("model", identity.get("model_id")))
            source_revision = p.get("revision", identity.get("revision"))
            if source_model != MODEL or source_revision != REVISION:
                result["errors"].append("source receipt model_id/revision mismatch")
            expected_payloads = payload_manifest(p)
            if not expected_payloads:
                result["errors"].append("source receipt has no parseable payload size/SHA manifest")
        except (OSError, json.JSONDecodeError) as exc:
            result["errors"].append(f"invalid source receipt: {exc}")
    inventory = []
    symlinks = []
    for path in sorted(incoming.rglob("*")):
        if path.is_symlink():
            symlinks.append({"path": str(path.relative_to(incoming)), "target": os.readlink(path)})
        elif path.is_file() and path.name != "C16_ASSET_VALIDATION.json":
            inventory.append({"path": str(path.relative_to(incoming)), "size": path.stat().st_size, "sha256": digest(path)})
    result["inventory"] = inventory
    result["source_receipt"] = str(source_receipt) if source_receipt else None
    result["symlinks"] = symlinks
    if symlinks:
        result["errors"].append("symlinks require explicit review; no promotion")
    names = {entry["path"] for entry in inventory}
    required = {"config.json", "tokenizer_config.json"}
    missing = sorted(required - names)
    if missing:
        result["errors"].append("missing required files: " + ",".join(missing))
    if not any(name.endswith(".safetensors") or name.startswith("pytorch_model") for name in names):
        result["errors"].append("no recognized weight payload")
    for name in ("config.json", "tokenizer_config.json"):
        candidate = incoming / name
        if candidate.is_file():
            try:
                json.loads(candidate.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                result["errors"].append(f"invalid {name}: {exc}")
    observed = {entry["path"]: {"size": entry["size"], "sha256": entry["sha256"]} for entry in inventory}
    if expected_payloads and observed != expected_payloads:
        result["errors"].append("incoming payload manifest differs from authoritative source receipt")
    if not result["errors"]:
        result["status"] = "U4_LOCAL_ASSET_EXACT_CLOSURE_PASS"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--incoming", type=Path, default=Path(f"/data/c16/models/.incoming/Llama-3.2-1B/{REVISION}"))
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite output")
    result = validate(args.incoming, args.authority, args.source_receipt)
    if args.promote:
        destination = args.incoming.parents[2] / f"Llama-3.2-1B@{REVISION}"
        if result["status"] != "U4_LOCAL_ASSET_EXACT_CLOSURE_PASS":
            result["errors"].append("promotion refused: validation not closed")
        elif destination.exists():
            result["errors"].append("promotion refused: destination already exists")
        else:
            shutil.move(str(args.incoming), str(destination))
            result["promoted_to"] = str(destination)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "output": str(args.output)}, sort_keys=True))
    return 0 if result["status"] == "U4_LOCAL_ASSET_EXACT_CLOSURE_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
