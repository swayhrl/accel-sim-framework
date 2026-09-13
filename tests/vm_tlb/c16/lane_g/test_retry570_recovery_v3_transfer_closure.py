import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_transfer_closure.py"
spec = importlib.util.spec_from_file_location("recovery_v3_transfer_closure", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_compare_accepts_identical_closed_sets():
    sha = hashlib.sha256(b"immutable").hexdigest()
    module.compare({"a": (9, sha)}, {"a": (9, sha)})


def test_compare_rejects_missing_or_changed_payload():
    sha = hashlib.sha256(b"immutable").hexdigest()
    try:
        module.compare({"a": (9, sha)}, {"b": (9, sha)})
    except module.ContractError:
        pass
    else:
        raise AssertionError("transfer closure must reject different sets")
