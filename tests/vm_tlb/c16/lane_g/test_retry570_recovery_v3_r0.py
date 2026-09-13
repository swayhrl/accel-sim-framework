import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_r0.py"
spec = importlib.util.spec_from_file_location("recovery_v3_r0", PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_authority_rows_preserve_every_authoritative_and_extension_row():
    rows = module.authority_rows()
    assert len(rows) == 32
    assert {row["deployment"] for row in rows} == {item[0] for item in module.DEPLOYMENTS}
    inherited = [row for row in rows if row["r0_status"] == "INHERITED_COMPLETE"]
    assert len(inherited) == 1
    assert inherited[0]["deployment"] == "llama_3p2_1b"
    assert inherited[0]["scenario"] == "S0"


def test_qwen_raw_and_awq_are_distinct_deployments():
    rows = module.authority_rows()
    raw = {row["exact_identity"] for row in rows if row["deployment"] == "qwen2p5_7b_instruct_raw"}
    awq = {row["exact_identity"] for row in rows if row["deployment"] == "qwen2p5_7b_instruct_awq"}
    assert raw != awq
