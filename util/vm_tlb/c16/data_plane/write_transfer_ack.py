#!/usr/bin/env python3
"""Write an immutable PASS-only transfer ACK after catalog admission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .receiver_common import AdmissionError, load_json, sha256_file, utc_now, write_json_new
except ImportError:
    from receiver_common import AdmissionError, load_json, sha256_file, utc_now, write_json_new


def write_ack(root: Path, admission_receipt: Path) -> tuple[Path, dict]:
    admission = load_json(admission_receipt)
    if admission.get("admission_status") != "PASS":
        raise AdmissionError("PASS admission receipt required before ACK")
    catalog = Path(admission["catalog_entry_path"])
    raw = Path(admission["destination_raw_path"])
    if not catalog.is_file() or not raw.is_dir():
        raise AdmissionError("catalog/raw closure absent; refusing ACK")
    if sha256_file(catalog) != admission.get("catalog_entry_sha256"):
        raise AdmissionError("catalog entry changed after admission")
    ack = {
        "schema_version": 1,
        "run_id": admission["run_id"],
        "source_manifest_sha256": admission["source_manifest_sha256"],
        "destination_manifest_or_verification_sha256": sha256_file(admission_receipt),
        "file_count": admission["file_count"],
        "total_bytes": admission["total_bytes"],
        "destination_raw_path": admission["destination_raw_path"],
        "verified_at_utc": utc_now(),
        "verification_status": "PASS",
        "catalog_entry_sha256": admission["catalog_entry_sha256"],
    }
    destination = root / "reports" / "transfer_acks" / f"{ack['run_id']}.TRANSFER_ACK.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_json_new(destination, ack)
    return destination, ack


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--admission-receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        path, ack = write_ack(args.root, args.admission_receipt)
        print(json.dumps({"verification_status": "PASS", "ack": str(path), "run_id": ack["run_id"]}, sort_keys=True))
        return 0
    except (AdmissionError, OSError) as exc:
        print(json.dumps({"verification_status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
