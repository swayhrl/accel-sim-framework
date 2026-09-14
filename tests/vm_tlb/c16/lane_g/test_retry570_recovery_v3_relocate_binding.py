import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_relocate_binding.py"
spec = importlib.util.spec_from_file_location("relocate_binding", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def binding_for(payload: Path, token: Path) -> dict:
    return {
        "schema_version": "C16_G_RUNTIME_FROZEN_BINDING_V1", "status": "FROZEN_RUNTIME_BINDING_READY",
        "scientific_eligible": False, "deployment_id": "c16_qwen25_7b_awq", "model_id": "Qwen/test",
        "model_revision": "a" * 40, "tokenizer_revision": "a" * 40, "scenario": {"scenario_id": "S1"},
        "input": {"class": "CODE", "derived_token_ids_sha256": hashlib.sha256(token.read_bytes()).hexdigest()},
        "model_path": "/old", "model_files": [{"path": "models/x/model.bin", "size_bytes": payload.stat().st_size,
                                                       "sha256": hashlib.sha256(payload.read_bytes()).hexdigest()}],
        "package_id": "P3", "package_fixed_commit": "b" * 40,
        "package_manifest_sha256": "c" * 64, "wheelhouse_manifest_sha256": "d" * 64,
    }


def test_verify_model_root_accepts_exact_bound_payload(tmp_path: Path):
    root = tmp_path / "model"; root.mkdir(); payload = root / "model.bin"; payload.write_bytes(b"model")
    token = tmp_path / "token.json"; token.write_text("[1]", encoding="utf-8")
    assert module.verify_model_root(binding_for(payload, token), root)[0]["sha256"] == hashlib.sha256(b"model").hexdigest()


def test_verify_model_root_rejects_wrong_payload_hash(tmp_path: Path):
    root = tmp_path / "model"; root.mkdir(); payload = root / "model.bin"; payload.write_bytes(b"model")
    token = tmp_path / "token.json"; token.write_text("[1]", encoding="utf-8")
    binding = binding_for(payload, token); payload.write_bytes(b"wrong")
    try:
        module.verify_model_root(binding, root)
    except module.ContractError:
        pass
    else:
        raise AssertionError("wrong relocated payload must fail closed")
