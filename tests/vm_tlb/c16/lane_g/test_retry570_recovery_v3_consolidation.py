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


def test_legacy_p1_network_receipt_is_not_mislabeled_as_local_copy(tmp_path: Path):
    root, receipts = tmp_path / "bulk", tmp_path / "receipts"; (root / "models/qwen2p5_0p5b_instruct/rev").mkdir(parents=True); receipts.mkdir()
    (receipts / "R1_QWEN2P5_0P5B_ASSET_RECEIPT.json").write_text('{"payloads":[],"destination":"/root/share/c16_recovery_v3/models/qwen2p5_0p5b_instruct/rev","all_payloads_size_sha256_closed":true}', encoding="utf-8")
    row = module.asset_row("qwen2p5_0p5b_instruct", "x", root, receipts)
    assert row["status"] == "ALREADY_UNDER_BULK_ROOT"
    assert row["migration_method"] == "EXACT_IMMUTABLE_NETWORK_FETCH"


def test_qwen3_partial_bulk_destination_is_explicitly_in_progress(tmp_path: Path):
    root, receipts = tmp_path / "bulk", tmp_path / "receipts"
    (root / "models/qwen3_8b/revision").mkdir(parents=True)
    receipts.mkdir()
    row = module.asset_row("qwen3_8b", "x", root, receipts)
    assert row["status"] == "EXACT_FETCH_IN_PROGRESS"
    assert row["hash_closure"] == "PENDING"


def test_qwen3_closed_receipt_is_registered_as_bulk_root_asset(tmp_path: Path):
    root, receipts = tmp_path / "bulk", tmp_path / "receipts"
    (root / "models/qwen3_8b/revision").mkdir(parents=True)
    receipts.mkdir()
    (receipts / "R1_QWEN3_8B_ASSET_RECEIPT.json").write_text(
        '{"payloads":[{"size_bytes":17}],"destination":"/root/share/c16_recovery_v3/models/qwen3_8b/revision","all_payloads_size_sha256_closed":true}',
        encoding="utf-8",
    )
    row = module.asset_row("qwen3_8b", "x", root, receipts)
    assert row["status"] == "ALREADY_UNDER_BULK_ROOT"
    assert row["destination_bytes"] == "17"
