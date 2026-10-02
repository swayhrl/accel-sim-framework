#!/usr/bin/env python3
"""NequIP official AOT compile pipeline with one opt-in deterministic OEQ bridge."""

import hashlib
import importlib
import json
import os
import traceback
from pathlib import Path

from deterministic_patch import enable_deterministic_oeq_for_packaged_oam_s


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
PACKAGE = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"
DATA_PATH = ROOT / "compile/DISCOVERY_DETERMINISTIC_FROZEN_INPUT.nequip_data.pt"
OUTPUT = ROOT / "compile/DREADY_OAM_S.nequip.pt2"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    from nequip.data import AtomicDataDict
    from nequip.data._key_registry import get_field_type, register_fields
    compile_mod = importlib.import_module("nequip.scripts.compile")
    original_modify = compile_mod.modify
    target = compile_mod.COMPILE_TARGET_DICT["ase"]
    original_inputs = list(target["input"])
    perm_key = AtomicDataDict.EDGE_TRANSPOSE_PERM_KEY
    if perm_key in original_inputs or original_inputs != ["pos", "edge_index", "atom_types", "cell", "edge_cell_shift"]:
        raise RuntimeError("Official ASE AOT input signature changed")
    if sha(DATA_PATH) != "1b6ebc0613a4581aa599d926befd9014a90a92a9d9d18794833ed2012cb72e6b":
        raise RuntimeError("Frozen deterministic compile data-path identity changed")
    if get_field_type(perm_key, error_on_unregistered=False) is None:
        register_fields(edge_fields=[perm_key], long_fields=[perm_key])
    if get_field_type(perm_key) != "edge":
        raise RuntimeError("Source-backed transpose permutation field registration failed")
    status = {"status": "STARTED", "model_package_sha256": sha(PACKAGE),
              "frame_index": 55, "natural_graph_sha256": sha(RAW / "DISCOVERY_NATURAL_GRAPH.npz"),
              "prepared_graph_sha256": sha(RAW / "DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz"),
              "candidate_patch_sha256": sha(Path(__file__).with_name("deterministic_patch.py")),
              "compile_data_path_sha256": sha(DATA_PATH),
              "compile_mode": "official_NequIP_AOTInductor_ase_cuda_TF32_OFF_with_one_required_perm_input",
              "official_A0_original_input_keys": original_inputs,
              "candidate_input_keys": original_inputs + [perm_key],
              "compile_field_registration": "edge_transpose_perm=edge-aligned int64; exact source key_registry.register_fields",
              "model_weight_change": False,
              "patch_receipts": []}
    (RAW / "DREADY_AOT_COMPILE_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")

    def research_modify(model, modifiers):
        result = original_modify(model, modifiers)
        status["patch_receipts"] = enable_deterministic_oeq_for_packaged_oam_s(result)
        (RAW / "DREADY_AOT_COMPILE_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
        return result

    compile_mod.modify = research_modify
    target["input"] = original_inputs + [perm_key]
    try:
        compile_mod.main([
            str(PACKAGE), str(OUTPUT),
            "--mode", "aotinductor", "--device", "cuda", "--target", "ase",
            "--modifiers", "enable_OpenEquivariance", "--no-tf32",
            "--data-path", str(DATA_PATH),
        ])
        if not OUTPUT.is_file() or OUTPUT.stat().st_size == 0:
            raise RuntimeError("AOT compile returned without candidate artifact")
        status.update({"status": "DREADY_AOT_COMPILED", "output_bytes": OUTPUT.stat().st_size,
                       "output_sha256": sha(OUTPUT)})
    except Exception as exc:
        status.update({"status": "DREADY_AOT_COMPILE_FAILED", "error_type": type(exc).__name__,
                       "error": str(exc), "traceback_tail": traceback.format_exc()[-15000:]})
    finally:
        compile_mod.modify = original_modify
        target["input"] = original_inputs
    (RAW / "DREADY_AOT_COMPILE_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: status.get(k) for k in ("status", "patch_receipts", "output_bytes", "output_sha256", "error_type", "error")}, default=str), flush=True)
    if status["status"] != "DREADY_AOT_COMPILED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
