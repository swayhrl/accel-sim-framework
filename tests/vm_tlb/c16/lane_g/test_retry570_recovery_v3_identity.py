import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_identity.py"
spec = importlib.util.spec_from_file_location("recovery_v3_identity", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_identity_authority_has_exact_distinct_raw_and_awq_qwen7():
    data = {row["deployment"]: row for row in module.rows()}
    assert data["qwen2p5_7b_instruct_raw"]["model_id"] != data["qwen2p5_7b_instruct_awq"]["model_id"]
    assert data["qwen2p5_7b_instruct_raw"]["revision"] != data["qwen2p5_7b_instruct_awq"]["revision"]


def test_glm_is_not_silently_guessed():
    glm = next(row for row in module.rows() if row["deployment"] == "glm_extension")
    assert glm["model_id"] == "UNRESOLVED"
    assert glm["r1_identity_status"] == "IDENTITY_UNRESOLVED_AFTER_AUTHORITY_SEARCH"
