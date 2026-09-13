import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_asset_search.py"
spec = importlib.util.spec_from_file_location("recovery_v3_asset_search", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_materialized_exact_config_is_found_without_move(tmp_path: Path):
    model = tmp_path / "model"; model.mkdir(); config = model / "config.json"; config.write_text('{"model_type":"test"}', encoding="utf-8")
    digest = module.sha256_file(config)
    found = module.search([tmp_path], digest)
    assert len(found) == 1
    assert found[0]["source_kind"] == "MATERIALIZED_MODEL_DIRECTORY"
    assert found[0]["destructive_move_forbidden"] is True


def test_hf_snapshot_reports_cache_root_not_snapshot_leaf(tmp_path: Path):
    config = tmp_path / "hub/models--org--model/snapshots/revision/config.json"; config.parent.mkdir(parents=True); config.write_text("{}", encoding="utf-8")
    found = module.search([tmp_path], module.sha256_file(config))
    assert found[0]["source_root"].endswith("models--org--model")
    assert "WHOLE_CACHE" in found[0]["source_kind"]
