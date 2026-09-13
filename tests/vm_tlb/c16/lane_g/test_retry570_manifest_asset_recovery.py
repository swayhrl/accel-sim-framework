import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_manifest_asset_recovery.py"
spec = importlib.util.spec_from_file_location("manifest_asset_recovery", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_copy_from_closed_source_preserves_source_and_closes_destination(tmp_path: Path):
    source, dest = tmp_path / "source", tmp_path / "dest"; source.mkdir(); dest.mkdir()
    payload = source / "model.safetensors"; payload.write_bytes(b"immutable")
    row = {"filename": payload.name, "size_bytes": payload.stat().st_size, "sha256": hashlib.sha256(payload.read_bytes()).hexdigest()}
    module.copy_from_closed_source(source, dest, [row])
    assert payload.read_bytes() == b"immutable"
    assert (dest / payload.name).read_bytes() == b"immutable"


def test_copy_from_closed_source_rejects_bad_source_before_copy(tmp_path: Path):
    source, dest = tmp_path / "source", tmp_path / "dest"; source.mkdir(); dest.mkdir()
    (source / "x").write_bytes(b"wrong")
    try:
        module.copy_from_closed_source(source, dest, [{"filename": "x", "size_bytes": 5, "sha256": "0" * 64}])
    except module.ContractError:
        pass
    else:
        raise AssertionError("bad source must fail before copying")
    assert not list(dest.iterdir())
