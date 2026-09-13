import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_exact_fetch.py"
spec = importlib.util.spec_from_file_location("recovery_v3_exact_fetch", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_close_requires_hub_size_and_lfs_hash(tmp_path: Path):
    payload = tmp_path / "weights.bin"; payload.write_bytes(b"immutable weights")
    sha = hashlib.sha256(payload.read_bytes()).hexdigest()
    closed = module.close(tmp_path, [{"filename": payload.name, "size_bytes": payload.stat().st_size, "hub_lfs_sha256": sha}])
    assert closed[0]["sha256"] == sha


def test_close_rejects_lfs_hash_mismatch(tmp_path: Path):
    (tmp_path / "weights.bin").write_bytes(b"immutable weights")
    try:
        module.close(tmp_path, [{"filename": "weights.bin", "size_bytes": 17, "hub_lfs_sha256": "0" * 64}])
    except module.ContractError:
        pass
    else:
        raise AssertionError("wrong immutable LFS hash must fail closed")


def test_inside_bulk_root(tmp_path: Path):
    root = tmp_path / "bulk"; root.mkdir()
    assert module.inside(root / "models" / "m", root)
    assert not module.inside(tmp_path / "elsewhere", root)


def test_fetch_source_declares_resume_as_explicit_opt_in():
    source = PATH.read_text(encoding="utf-8")
    assert "--resume-partial" in source
    assert "without --resume-partial" in source
    assert "exist_ok=args.resume_partial" in source
