import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_existing_asset_copy.py"
spec = importlib.util.spec_from_file_location("existing_asset_copy", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_model_rows_accept_only_closed_model_assets():
    receipt = {"rows": [
        {"artifact_id": "c16_llama:model.safetensors", "destination_relpath": "models/x/model.safetensors", "size_bytes": 3,
         "sha256": "a" * 64, "status": "PASS"},
        {"artifact_id": "A_INPUT:TEXT", "destination_relpath": "a_assets/inputs/TEXT.txt", "size_bytes": 1,
         "sha256": "b" * 64, "status": "PASS"},
    ]}
    assert module.expected_model_rows(receipt) == [{"filename": "model.safetensors", "size_bytes": 3, "sha256": "a" * 64}]


def test_model_rows_reject_unclosed_model_asset():
    receipt = {"rows": [{"artifact_id": "c16_llama:model.safetensors", "destination_relpath": "model.safetensors", "size_bytes": 3,
                           "sha256": "a" * 64, "status": "FAIL"}]}
    try:
        module.expected_model_rows(receipt)
    except module.ContractError:
        pass
    else:
        raise AssertionError("unclosed source row must be rejected")
