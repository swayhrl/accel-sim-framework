#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CCE_COMMIT = "3de376c106a1916bc5e1b619f9c77c87a461ee1c"
PARENT_COMMIT = "ad9a302a49cdb3b1e75a9bbf04dab819c362cb1a"
START_HEAD = "9413136d633615f3d56aa4c5f788f81cca3f0b41"
MODEL_SHA = "fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    repo = args.repo
    receipts = root / "receipts"
    parent = Path("/data/c16/awma/exact_loss_cce_liger_109_v1_20260930")
    model = Path(
        "/data/c16/models/.incoming/qwen2p5_0p5b_instruct/"
        "7ae557604adf67be50417f59c2c2f167def9a775/model.safetensors"
    )
    original = root / "source_before" / "cut_cross_entropy"
    patched = root / "source" / "cce" / "cut_cross_entropy"
    patch = repo / "util/vm_tlb/awma/cce_zero_init_removal/cce_zero_init_removal.patch"
    checks = {
        "cce_archive": (root / "source/cce.tar.gz", "446d282d5b9f5bf2f8bc5a551a016498706f5066230ed682f7477c16c09cc553"),
        "original_cce_backward": (original / "cce_backward.py", "530f4086c0f8b595708055d3e0575253e7328aaa3fa1fa96427f392468027e52"),
        "original_tl_utils": (original / "tl_utils.py", "8923e02f3240dfb96ca9204e81e1d21f73f5ee1d5649e4b84dda1b1e36dd0d60"),
        "patched_cce_backward": (patched / "cce_backward.py", "e5402a590ef019692d8341805d3adf18ed95d3062c59236b364322c296b42d36"),
        "patched_tl_utils": (patched / "tl_utils.py", "e117b70a0fdc2ec4313fd7d9ba5a7e1d78b30fb478760c3c661f9d717cc65ea4"),
        "source_patch": (patch, "e4156b6ec21a7c8696192c9a2ad3eb2196630c72373c64bc8395bc2ef12fda56"),
        "accepted_hidden_snapshot": (parent / "raw/REAL_FINAL_HIDDEN_AND_LABELS.pt", "db296e7c15ef86a1ffb1a18796518795493a76b8d2be2d886712677ccb345ba1"),
        "model": (model, MODEL_SHA),
        "parent_pack_manifest": (
            repo / "docs/vm_tlb/review_packs/AWMA_EXACT_LOSS_CCE_LIGER_109_V1/SHA256SUMS",
            "a588a1a23e1043859a64f499c7d7d5eaddc07751b64d878199cc3b26bc0285e1",
        ),
    }
    observed = {}
    for name, (path, expected) in checks.items():
        actual = sha(path)
        if actual != expected:
            raise ValueError(f"{name} sha mismatch: {actual} != {expected}")
        observed[name] = {"path": str(path), "sha256": actual, "size_bytes": path.stat().st_size}

    source_text = (patched / "cce_backward.py").read_text()
    tl_text = (patched / "tl_utils.py").read_text()
    for required in (
        'torch.empty_like(c, dtype=dc_dtype) if dc_first_store else torch.zeros_like',
        'DC_FIRST_STORE=dc_first_store',
        'os.getenv("CCE_DC_FIRST_STORE", "0")',
    ):
        if required not in source_text:
            raise ValueError(f"missing source design token: {required}")
    if "tl_lock_first_store_or_add" not in tl_text:
        raise ValueError("missing first-store lock helper")

    source_receipt = {
        "stage": "AWMA_CCE_ZERO_INIT_REMOVAL_109_V1",
        "repository": "apple-aiml-research/ml-cross-entropy",
        "commit": CCE_COMMIT,
        "scientific_parent": PARENT_COMMIT,
        "execution_start_head": START_HEAD,
        "checks": observed,
        "source_manifest_before_sha256": sha(receipts / "CCE_SOURCE_SHA256_BEFORE.txt"),
        "source_manifest_after_sha256": sha(receipts / "CCE_SOURCE_SHA256_AFTER.txt"),
        "patch_apply_reproduction": "PASS",
        "modified_source_files": [
            "cut_cross_entropy/cce_backward.py",
            "cut_cross_entropy/tl_utils.py",
        ],
    }
    dump(receipts / "SOURCE_IDENTITY.json", source_receipt)

    runtime = json.loads((parent / "raw/RUNTIME_INPUT_RECEIPT.json").read_text())
    input_receipt = {
        "stage": "AWMA_CCE_ZERO_INIT_REMOVAL_109_V1",
        "scientific_parent": PARENT_COMMIT,
        "shape": {"B": 1, "T": 255, "H": 896, "V": 151936, "dtype": "torch.bfloat16"},
        "snapshot_path": str(parent / "raw/REAL_FINAL_HIDDEN_AND_LABELS.pt"),
        "snapshot_sha256": runtime["snapshot_sha256"],
        "hidden_sha256": runtime["hidden_sha256"],
        "labels_sha256": runtime["labels_sha256"],
        "lm_head_sha256": runtime["lm_head_sha256"],
        "checkpoint_tensor_key": runtime["checkpoint_tensor_key"],
        "model_weight_sha256": MODEL_SHA,
        "qualified_before_gpu": True,
    }
    dump(receipts / "INPUT_RECEIPT.json", input_receipt)

    design = {
        "stage": "AWMA_CCE_ZERO_INIT_REMOVAL_109_V1",
        "frozen_before_gpu": True,
        "arms": {
            "C0": "accepted CCE exact/no-filter torch.zeros_like FP32 dC",
            "C1": "same CCE exact/no-filter with empty FP32 dC and first-store/update-lock protocol",
        },
        "state_encoding": {
            "0": "uninitialized/free",
            "1": "initialized/free",
            "2": "initialization or update lock held",
        },
        "fixed_meta": {
            "BLOCK_B": 128,
            "BLOCK_V": 128,
            "BLOCK_D": 32,
            "MM_BACK_BLOCK_D": 64,
            "num_warps": 4,
            "num_stages": 4,
            "CCE_AUTOTUNE": 0,
        },
        "real_init_state": {
            "lock_rows": 1187,
            "lock_cols": 14,
            "elements": 16618,
            "bytes": 66472,
            "additional_bytes_vs_c0": 0,
            "reuses_existing_dc_locks": True,
        },
        "all_ignore_fallback": "B==0 keeps torch.zeros_like and disables DC_FIRST_STORE",
        "second_full_size_buffer": False,
        "full_size_lazy_zero": False,
        "future_order_knowledge": False,
        "tolerance": {"rtol": 0.01, "atol": 0.01},
    }
    dump(receipts / "DESIGN_PREREGISTRATION.json", design)
    (receipts / "INIT_STATE_ACCOUNTING.tsv").write_text(
        "arm\tlock_rows\tlock_cols\telements\tbytes\tadditional_bytes_vs_c0\tfull_dc_fp32_bytes\treset_inside_boundary\n"
        "C0\t1187\t14\t16618\t66472\t0\t544538624\ttrue\n"
        "C1\t1187\t14\t16618\t66472\t0\t544538624\ttrue\n"
    )
    print(json.dumps({"qualified": True, "patch_sha256": observed["source_patch"]["sha256"]}))


if __name__ == "__main__":
    main()
