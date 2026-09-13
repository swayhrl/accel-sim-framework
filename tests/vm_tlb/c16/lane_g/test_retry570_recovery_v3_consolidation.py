import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_consolidation.py"
spec = importlib.util.spec_from_file_location("recovery_v3_consolidation", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_user_excluded_qwen3_30b_is_not_a_blocker_or_skip(tmp_path: Path):
    row = module.asset_row("qwen3_30b_a3b", "x", tmp_path, tmp_path)
    assert row["status"] == "EXCLUDED_BY_USER_CURRENT_CAMPAIGN"
    assert "BLOCKED" not in row["status"] and "SKIPPED" not in row["status"]


def test_glm_remains_unresolved_without_variant_guess(tmp_path: Path):
    row = module.asset_row("glm_extension", "UNRESOLVED", tmp_path, tmp_path)
    assert row["status"] == "IDENTITY_NOT_YET_RESOLVED"
