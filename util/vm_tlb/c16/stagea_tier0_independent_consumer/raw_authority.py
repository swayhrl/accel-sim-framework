"""Freeze and independently verify Stage A contract/producer raw authority."""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from core import audit_raw_index


CONTRACT_SHA256 = "a71349283b1661cb23d86cc61dfad6ab5ea2cd8752ca4252bbc1d2feee5acb08"
EXPECTED_COMMITS = {
    "scope_revision_commit": "137e3414c9c8e59cf1b167e5acc14149fb6273d6",
    "awq_observer_v2_runtime_pass_commit": "9d5aa2f36e22a1a8fcc253d6df865160b5dba797",
    "asset_input_closure_commit": "c3f625e46adb8d5c4082ded8b61858c710e1f4e9",
    "runtime_qualification_commit": "3f62f909a474e4c56695ffacf36ddcb5d7b5f147",
    "observer_v2_source_commit": "f63d39c8d90ced038445c264fa8242c524a1aa6f",
    "olmoe_diagnostic_commit": "8b677cfa541877f559614f7bf22a40dd11cebd56",
}
POINT_ALLOWLIST = ["MP01", "MP02", "MP03", "MP05"]


def digest_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_final_contract(contract_pack: str | Path) -> dict:
    pack = Path(contract_pack)
    contract_path = pack / "C16_STAGEA_DENSE_FIRST_TIER0_109_CONTRACT_V1.json"
    if digest_file(contract_path) != CONTRACT_SHA256:
        raise ValueError("final contract SHA mismatch")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    decision = json.loads((pack / "FINAL_DECISION.json").read_text(encoding="utf-8"))
    if decision["status"] != "STAGEA_DENSE_FIRST_TIER0_CONTRACT_FINALIZED" or not decision["execution_authorized"]:
        raise ValueError("contract not finalized/authorized")
    if not contract["execution_authorized"] or contract["status"] != "AUTHORIZED_BY_PROJECT_REVIEW":
        raise ValueError("contract authorization mismatch")
    if contract["point_allowlist_in_order"] != POINT_ALLOWLIST or contract["gpu_budget"]["total_gpu_active_seconds_cap"] != 540:
        raise ValueError("point/budget contract changed")
    if any(contract["authority"].get(k) != v for k, v in EXPECTED_COMMITS.items()):
        raise ValueError("upstream authority commit changed")
    estimator = contract["matched_graph_control_gap"]
    if estimator["only_predefined_pair"] != ["MP02", "MP03"]:
        # The schema freezes threshold in stop_rules; no dynamic estimator substitution.
        raise ValueError("matched Graph pair changed")
    if contract["stop_rules"]["graph_control_absorption_gte"] != 0.85:
        raise ValueError("Graph absorption threshold changed")
    return contract


def load_producer_raw_authority(producer_pack: str | Path, contract: dict) -> dict:
    pack = Path(producer_pack)
    decision = json.loads((pack / "FINAL_DECISION.json").read_text(encoding="utf-8"))
    if decision.get("status") not in {"STAGEA_TIER0_PRODUCER_COMPLETE", "STAGEA_TIER0_PRODUCER_PARTIAL"}:
        raise ValueError("producer is not terminal COMPLETE/PARTIAL")
    if decision.get("automatic_next_goal") is not False:
        raise ValueError("producer automatic-next-goal receipt not false")
    run_id = decision.get("run_id")
    if not isinstance(run_id, str) or not run_id or "/" in run_id or "\\" in run_id or run_id in {".", ".."}:
        raise ValueError("invalid producer run id")
    root_template = contract["durable_publish"]["durable_root"]
    durable_root = root_template.replace("<run_id>", run_id)
    if "<" in durable_root or not durable_root.startswith("/root/share/mnt164/huangrulin/c16_ai_workload/measurement_campaign/stagea_dense_first_tier0_v1/"):
        raise ValueError("invalid durable raw root")
    index_path = pack / "RAW_INDEX.tsv"
    raw_audit = audit_raw_index(str(index_path), durable_root)
    if any(row["status"] != "PASS" for row in raw_audit):
        raise ValueError("durable raw size/SHA failure")
    artifact_paths = {row["artifact"]: row["path"] for row in raw_audit}
    if len(artifact_paths) != len(raw_audit):
        raise ValueError("duplicate raw artifact")
    return {
        "decision": decision,
        "run_id": run_id,
        "durable_root": durable_root,
        "raw_index_sha256": digest_file(index_path),
        "raw_audit": raw_audit,
        "artifact_paths": artifact_paths,
    }
