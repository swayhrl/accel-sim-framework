#!/usr/bin/env python3
"""Create a byte-identical L2 input authority under exact LDC semantics."""

from __future__ import annotations

import hashlib
import json
import lzma
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


SOURCE = Path(
    "/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/"
    "ai_translation_native_atlas_capture_20260926/capture_L2/raw/"
    "kernel-7062-ctx_0x5c4fa771e8b0.traceg.xz"
)
CANARY = Path(
    "/root/awma_intrawarp_translation_baseline_residual_v1_runtime/inputs/"
    "kernel-17543-ctx_0x5be0856adcb0.traceg.xz"
)
VALIDATOR = Path(
    "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/"
    "l2_grammar_audit/traceg_grammar_smoke"
)
OUTPUT = Path(
    "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/"
    "L2_GRAMMAR_REPAIRED_DETERMINISTIC"
)
SOURCE_SHA = "db391d6731d0568a0abf0283546c564d793adc0fbeecab7010831eb8329297e6"
VALIDATOR_SOURCE_SHA = "135761ac8e10a7fb6c98a3413cd477602d84b164a778c5d4f2a1bfb517be5b37"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def ldc_forms(path: Path) -> tuple[int, dict[str, int]]:
    count = 0
    forms: dict[str, int] = {}
    with lzma.open(path, "rt", errors="strict") as stream:
        for raw in stream:
            if "LDC.U8" not in raw:
                continue
            parts = raw.split()
            destinations = int(parts[2])
            opcode_index = 3 + destinations
            if parts[opcode_index] != "LDC.U8":
                raise RuntimeError("LDC.U8 token was not in opcode position")
            sources = int(parts[opcode_index + 1])
            width_index = opcode_index + 2 + sources
            width = int(parts[width_index])
            suffix = parts[width_index + 1 :]
            # Trace-v5 implicit LDC record: no dynamic address payload and one
            # immediate token. U8 still deterministically encodes one byte in
            # the opcode, while the accepted consumer handles OP_LDC through
            # its historical constant-space approximation.
            if width != 0 or suffix != ["0"]:
                raise RuntimeError(f"ambiguous LDC.U8 form: {raw.rstrip()}")
            key = f"width={width};suffix={' '.join(suffix)}"
            forms[key] = forms.get(key, 0) + 1
            count += 1
    return count, forms


def validate(path: Path) -> dict:
    completed = subprocess.run(
        [str(VALIDATOR), str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr)
    return json.loads(completed.stdout)


def main() -> int:
    if digest(SOURCE) != SOURCE_SHA:
        raise RuntimeError("source L2 trace SHA mismatch")
    if not VALIDATOR.is_file():
        raise RuntimeError("compiled validator missing")
    l2_count, l2_forms = ldc_forms(SOURCE)
    canary_count, canary_forms = ldc_forms(CANARY)
    if (
        l2_count != 256
        or canary_count == 0
        or set(l2_forms) != set(canary_forms)
    ):
        raise RuntimeError("LDC.U8 form/canary gate failed")
    l2_validation = validate(SOURCE)
    canary_validation = validate(CANARY)
    if l2_validation.get("status") != "TRACEG_GRAMMAR_PASS":
        raise RuntimeError("L2 validator did not pass")
    if canary_validation.get("status") != "TRACEG_GRAMMAR_PASS":
        raise RuntimeError("canary validator did not pass")
    if l2_validation["opcode_counts"].get("LDC.U8") != l2_count:
        raise RuntimeError("validator LDC.U8 count mismatch")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    derived = OUTPUT / "kernel-7062-ctx_0x5c4fa771e8b0.traceg.xz"
    shutil.copyfile(SOURCE, derived)
    if digest(derived) != SOURCE_SHA:
        raise RuntimeError("byte-identical derived trace gate failed")
    kernelslist = OUTPUT / "kernelslist.g"
    kernelslist.write_text(derived.name + "\n")
    receipt = {
        "authority": "L2_GRAMMAR_REPAIRED_DETERMINISTIC",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_path": str(SOURCE),
        "source_sha256": SOURCE_SHA,
        "derived_path": str(derived),
        "derived_sha256": digest(derived),
        "byte_identical": True,
        "modified_instruction_records": 0,
        "semantic_normalization_records": l2_count,
        "semantic_rule": (
            "exact base opcode LDC with width=0/no dynamic address is the "
            "accepted implicit constant-load consumer class; U8 encodes one "
            "byte but OP_LDC retains the existing trace-driven constant-space "
            "approximation and does not become a global VM request"
        ),
        "l2_ldc_u8_count": l2_count,
        "l2_forms": l2_forms,
        "canary_path": str(CANARY),
        "canary_sha256": digest(CANARY),
        "canary_ldc_u8_count": canary_count,
        "canary_forms": canary_forms,
        "validator_path": str(VALIDATOR),
        "validator_binary_sha256": digest(VALIDATOR),
        "validator_source_sha256": VALIDATOR_SOURCE_SHA,
        "l2_validator": l2_validation,
        "canary_validator": canary_validation,
        "kernelslist_path": str(kernelslist),
        "kernelslist_sha256": digest(kernelslist),
        "original_artifact_unchanged": digest(SOURCE) == SOURCE_SHA,
    }
    (OUTPUT / "AUTHORITY.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({
        "authority": receipt["authority"],
        "byte_identical": True,
        "ldc_u8_records": l2_count,
        "status": l2_validation["status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
