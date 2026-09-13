from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = (ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_package_inputs.py").read_text(encoding="utf-8")


def test_package_inputs_never_duplicate_model_weights():
    assert 'if row["kind"] == "MODEL_ASSET"' in SOURCE
    assert '"model_weights_not_duplicated": True' in SOURCE


def test_package_inputs_reuses_fixed_package_validator():
    assert "validate_metadata(args.package_commit, args.package_dir, args.package_manifest_sha256)" in SOURCE
    assert "asset receipt revision differs from fixed package identity" in SOURCE
