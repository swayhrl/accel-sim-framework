import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_binding_transfer_receipt.py"
spec = importlib.util.spec_from_file_location("binding_transfer_receipt", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_manifest_requires_exact_local_payload_hashes(tmp_path: Path):
    payload = tmp_path / "S1_CODE/token_ids.json"
    payload.parent.mkdir()
    payload.write_text("[1]", encoding="utf-8")
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    manifest = tmp_path / "REMOTE_SHA256_MANIFEST_V2.tsv"
    manifest.write_text(f"{digest}  S1_CODE/token_ids.json\n", encoding="utf-8")
    assert module.validate_manifest(tmp_path, manifest, hashlib.sha256(manifest.read_bytes()).hexdigest()) == ["S1_CODE/token_ids.json"]


def test_manifest_rejects_duplicate_payload_names(tmp_path: Path):
    payload = tmp_path / "x"; payload.write_text("x", encoding="utf-8")
    digest = hashlib.sha256(b"x").hexdigest()
    manifest = tmp_path / "m"
    manifest.write_text(f"{digest}  x\n{digest}  x\n", encoding="utf-8")
    try:
        module.validate_manifest(tmp_path, manifest, hashlib.sha256(manifest.read_bytes()).hexdigest())
    except module.ContractError:
        pass
    else:
        raise AssertionError("duplicate manifest name must be rejected")
