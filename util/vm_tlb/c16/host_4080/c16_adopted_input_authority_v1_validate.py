#!/usr/bin/env python3
"""CPU-only validator for the future-use C16 adopted Llama input authority."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

EXPECTED = {
    "TEXT.txt": "bae0b908106146659663fa04f44bc03ec0da18cadb08c9ec357c140afc4d8208",
    "TEXT_T128.json": "0b5a86fdee44452e74e5d80e8043ebd97054fbbe29a6232a4f5cf5d06568c7dd",
    "frozen_token_ids.json": "fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624",
    "canonical_target_token_ids": "f9cf1ea6dca7956c740b3aa0af59acadd17be014df2aaffb75d240383502e3a7",
}
IDENTITY = {
    "scenario_id": "S0", "batch_size": 1, "prefill_tokens": 128,
    "decode_tokens": 4, "input_class": "TEXT",
    "model_id": "meta-llama/Llama-3.2-1B",
    "model_revision": "4e20de362430cd3b72f300e6b0f18e50e7166e08",
}
FORBIDDEN_HISTORICAL_NAMES = {
    "LLAMA_S0_TEXT_TOKEN_IDS.json", "LLAMA_S0_TEXT_BINDING_RECEIPT.json",
    "C16_FIND_AND_TRANSFER_LLAMA_S5_FROZEN_INPUT_BINDING_RECEIPT.json",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite output")

    root = args.root
    errors = []
    actual = {}
    for name, expected in EXPECTED.items():
        if name == "canonical_target_token_ids":
            continue
        path = root / name
        if not path.is_file():
            errors.append(f"missing payload: {name}")
            continue
        actual[name] = {"size_bytes": path.stat().st_size, "sha256": sha256(path)}
        if actual[name]["sha256"] != expected:
            errors.append(f"payload SHA256 mismatch: {name}")

    receipt_path = root / "ADOPTED_INPUT_RECEIPT.json"
    receipt = {}
    if not receipt_path.is_file():
        errors.append("missing ADOPTED_INPUT_RECEIPT.json")
    else:
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("authority_type") != "FUTURE_USE_ADOPTED_INPUT_NOT_HISTORICAL_RECOVERY":
            errors.append("authority type is not adopted future-use authority")
        if receipt.get("semantic_identity") != IDENTITY:
            errors.append("semantic identity mismatch")
        if receipt.get("tokenizer_invoked") is not False:
            errors.append("receipt does not prove tokenizer_invoked=false")
        if receipt.get("no_historical_receipt_recreated") is not True:
            errors.append("receipt does not prove no historical receipt recreation")
        if receipt.get("future_use_only") is not True:
            errors.append("receipt does not prove future-use-only scope")
        if receipt.get("no_retroactive_change_to_rtx3090_or_rtx4080_r5") is not True:
            errors.append("receipt does not protect historical authority")
        if receipt.get("historical_recovery_status") != "HISTORICAL_FROZEN_INPUT_NOT_RECOVERED":
            errors.append("receipt changes historical recovery status")
        for name, expected in EXPECTED.items():
            if name == "canonical_target_token_ids":
                continue
            row = receipt.get("payloads", {}).get(name, {})
            if row.get("source_sha256") != expected or row.get("git_copy_sha256") != expected:
                errors.append(f"receipt source/copy SHA mismatch: {name}")

    try:
        target = json.loads((root / "TEXT_T128.json").read_text())["target_token_ids"]
        derived = json.loads((root / "frozen_token_ids.json").read_text())
        if not isinstance(target, list) or len(target) != 128 or not all(isinstance(x, int) and not isinstance(x, bool) for x in target):
            errors.append("target_token_ids is not a 128-element integer list")
        compact = json.dumps(target, separators=(",", ":"), ensure_ascii=False).encode()
        actual["canonical_target_token_ids"] = {"count": len(target) if isinstance(target, list) else None, "sha256": hashlib.sha256(compact).hexdigest()}
        if actual["canonical_target_token_ids"]["sha256"] != EXPECTED["canonical_target_token_ids"]:
            errors.append("canonical target_token_ids SHA256 mismatch")
        if derived != target:
            errors.append("frozen token IDs differ from target_token_ids")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"token payload parse failure: {exc}")

    for name in FORBIDDEN_HISTORICAL_NAMES:
        if (root / name).exists():
            errors.append(f"forbidden historical-recovery filename present: {name}")

    result = {
        "schema_version": 1,
        "validator": "c16_adopted_input_authority_v1_validate.py",
        "status": "ADOPTED_INPUT_AUTHORITY_V1_PASS" if not errors else "ADOPTED_INPUT_AUTHORITY_V1_FAIL",
        "errors": errors,
        "expected_hashes": EXPECTED,
        "actual": actual,
        "tokenizer_invoked": False,
        "historical_recovery_status": "HISTORICAL_FROZEN_INPUT_NOT_RECOVERED",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
