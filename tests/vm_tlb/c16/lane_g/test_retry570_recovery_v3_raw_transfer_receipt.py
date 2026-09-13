import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_raw_transfer_receipt.py"
spec = importlib.util.spec_from_file_location("raw_transfer_receipt", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def manifest(payload: Path) -> dict[str, object]:
    return {"payload": {"logical_path": "/gpu/raw/" + payload.name, "size_bytes": payload.stat().st_size, "sha256": hashlib.sha256(payload.read_bytes()).hexdigest()}}


def test_close_accepts_identical_remote_and_local_payload(tmp_path: Path):
    payload = tmp_path / "raw.nsys-rep"
    payload.write_bytes(b"closed payload")
    result = module.close(module.closed_remote_payload(manifest(payload)), payload)
    assert result["size_bytes"] == len(b"closed payload")


def test_close_rejects_mismatched_remote_payload(tmp_path: Path):
    payload = tmp_path / "raw.nsys-rep"
    payload.write_bytes(b"local")
    bad = manifest(payload)
    bad["payload"]["sha256"] = hashlib.sha256(b"different").hexdigest()
    try:
        module.close(module.closed_remote_payload(bad), payload)
    except module.ContractError:
        pass
    else:
        raise AssertionError("transfer receipt must fail closed on a SHA mismatch")


def test_closed_remote_payload_rejects_invalid_hash():
    try:
        module.closed_remote_payload({"payload": {"logical_path": "/gpu/x", "size_bytes": 1, "sha256": "not-a-hash"}})
    except module.ContractError:
        pass
    else:
        raise AssertionError("remote manifest needs a valid SHA256")
