import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_r5_closeout.py"
spec = importlib.util.spec_from_file_location("recovery_v3_r5_closeout", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_retained_raw_requires_every_manifest_hash_to_match(tmp_path: Path):
    (tmp_path / "payload").write_text("closed", encoding="utf-8")
    digest = hashlib.sha256(b"closed").hexdigest()
    manifest = tmp_path / "REMOTE_SHA256_MANIFEST.tsv"
    manifest.write_text(f"{digest}  payload\n", encoding="utf-8")
    proof = module.verify_retained_raw(tmp_path, manifest)
    assert proof["payload_count"] == 1
    assert proof["all_remote_local_payload_hashes_match"] is True


def test_budget_gate_requires_all_frozen_deployment_windows(tmp_path: Path):
    ledger = {"limits": {"nvbit_windows_per_deployment": 2}, "entries": [
        {"deployment_id": module.DEPLOYMENT, "operation_kind": "NVBIT", "run_id": "a"},
        {"deployment_id": module.DEPLOYMENT, "operation_kind": "NVBIT", "run_id": "b"},
    ]}
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(ledger), encoding="utf-8")
    result = module.verify_budget(path)
    assert result["consumed_nvbit_windows"] == 2
    assert result["budget_bypass"] is False
