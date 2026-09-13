import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_post_llama_dataset_closeout.py"
spec = importlib.util.spec_from_file_location("post_llama_closeout", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_validate_manifest_rejects_duplicate_payload_path(tmp_path: Path):
    (tmp_path / "payload.txt").write_text("x", encoding="utf-8")
    digest = module.sha256_file(tmp_path / "payload.txt")
    (tmp_path / "PUBLISH_MANIFEST.json").write_text(json.dumps({"payloads": [{"path": "payload.txt", "size_bytes": 1, "sha256": digest}, {"path": "payload.txt", "size_bytes": 1, "sha256": digest}]}), encoding="utf-8")
    (tmp_path / "PUBLISH_VALIDATION.json").write_text(json.dumps({"all_payloads_exist_size_sha256_match": True, "manifest_sha256": module.sha256_file(tmp_path / "PUBLISH_MANIFEST.json")}), encoding="utf-8")
    try:
        module.validate_manifest(tmp_path)
    except module.ContractError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate path must fail closed")


def test_payload_rows_excludes_self_validating_files(tmp_path: Path):
    (tmp_path / "a.json").write_text("{}", encoding="utf-8")
    (tmp_path / "PUBLISH_MANIFEST.json").write_text("{}", encoding="utf-8")
    (tmp_path / "PUBLISH_VALIDATION_RECEIPT.json").write_text("{}", encoding="utf-8")
    assert [row["path"] for row in module.payload_rows(tmp_path)] == ["a.json"]
