"""CPU-only candidate qualification. Writes only its own evidence files when run as a script."""
import ast
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def run():
    module_spec = importlib.util.spec_from_file_location("fixed_historical_candidate", HERE / "historical_provider.py")
    m = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(m)
    scope, _ = m._read(HERE / "SCOPE.json", m.SCOPE_SHA256)
    bs = scope["static_comparison_baseline"]
    registry, _ = m._read(scope["registry_path"])
    row = registry["registered_future_requests"][scope["request_id"]]["consumed"][bs["cohort"]]
    root = Path(bs["output"])
    docs = {"done": m._optional(bs["done_path"]), "exit": m._optional(root / "NATIVE_EXIT.json"),
            "point": m._optional(root / "ACCEPTED_POINT.json"), "bundle": m._optional(root / "VALIDATED_APPLICATION_BUNDLE.json"),
            "archive": m._optional(Path(bs["case_control"]) / "ARCHIVE_RECEIPT.json")}
    cases = []
    def check(name, condition):
        assert condition, name
        cases.append({"case": name, "passed": True})
    positive = m._terminal(bs, row, docs)
    check("existing_same_source_LAVAMD_S_strict_positive", positive["accepted"] and positive["cycles"] == 5581479 and positive["terminal"])
    empty = m._terminal(bs, row, {})
    check("missing_handle_and_terminal_not_termination", not empty["terminal"] and empty["cycles"] is None)
    wrong_row = dict(row, uuid="not-the-fixed-uuid")
    check("future_or_other_uuid_rejected", not m._terminal(bs, wrong_row, docs)["terminal"])
    for name, mutate in [
        ("wrong_input_rejected", lambda d: d["point"][0].update(input_identity_sha256="bad")),
        ("partial_cycle_rejected", lambda d: d["point"][0].update(cycles=None)),
        ("missing_validation_hold", lambda d: d.update(bundle=(None, None))),
        ("bad_restore_rejected", lambda d: d["archive"][0]["native_restores"][0].update(status="PENDING")),
        ("wrong_closed_generation_metadata_rejected", lambda d: d["done"][0]["closed_artifact_refs"]["NATIVE_SIMULATOR_PID_AND_MAPS.json"].update(sha256="bad")),
        ("wrong_source_rejected", lambda d: d["point"][0]["source_identity"].update(core_source_commit="bad")),
        ("option_contract_mismatch_rejected", lambda d: d["bundle"][0]["application"]["actual_options"].update({"-gpgpu_clock_domains":"bad"})),
        ("incomplete_raw_stream_rejected", lambda d: d["point"][0]["raw_stream_receipt"].update(complete_compressed_stream=False)),
    ]:
        fixture = copy.deepcopy(docs)
        mutate(fixture)
        result = m._terminal(bs, row, fixture)
        check(name, not result["accepted"] and not result["terminal"] and result["cycles"] is None)
    negative = copy.deepcopy(docs)
    for k in ["done", "exit"]:
        negative[k][0]["launcher_wait_returncode"] = -6
    negative["point"] = (None, None)
    nr = m._terminal(bs, dict(row, state="CLOSED_UNACCEPTED"), negative)
    check("explicit_own_negative_terminal_without_cycles", nr["status"] == "EXPLICIT_UNACCEPTED" and nr["terminal"] and nr["cycles"] is None)
    conflict = copy.deepcopy(docs)
    for k in ["done", "exit"]:
        conflict[k][0]["launcher_wait_returncode"] = -6
    cr = m._terminal(bs, row, conflict)
    check("positive_negative_conflict_stays_hold", not cr["terminal"])
    with patch.object(m, "_process", return_value={"handle_state":"HANDLE_MISSING_NOT_TERMINAL"}):
        obj = m._object(scope["objects"][0], registry["registered_future_requests"][scope["request_id"]]["consumed"][scope["objects"][0]["cohort"]])
    check("lost_live_handle_no_false_stop", not obj["terminal"] and obj["status"].startswith("HOLD"))
    reused = dict(scope["objects"][0], pid=os.getpid(), start_ticks=-1)
    check("PID_generation_reuse_not_followed", m._process(reused)["handle_state"] == "PID_REUSED_NOT_FOLLOWED")
    with patch.object(m, "_process", return_value={"handle_state":"SAME_GENERATION_LIVE", "cpu_progress_confirmed":False}):
        cl = m._object(bs, row)
    check("live_terminal_conflict_hold", cl["status"] == "HOLD_LIVE_TERMINAL_CONFLICT" and not cl["terminal"])
    with patch.object(m, "_pin_errors", return_value=["synthetic contract mismatch"]):
        pinbad = m._object(bs, row, observe_process=False)
    check("contract_SHA_mismatch_hold", pinbad["status"] == "HOLD_CONTRACT_UNVERIFIED" and not pinbad["terminal"])
    accepted_row = dict(positive)
    same = m._comparison(accepted_row, accepted_row, bs, bs)
    check("own_baseline_exact_one", same["cycles_over_baseline"] == 1.0)
    mismatch = m._comparison(accepted_row, accepted_row, bs, dict(bs, input_identity_sha256="other"))
    check("cross_input_comparison_not_filled", mismatch["cycles_over_baseline"] is None)
    tree = ast.parse((HERE / "historical_provider.py").read_text())
    calls = [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    forbidden = {"write_text", "write_bytes", "mkdir", "unlink", "rmdir", "rename", "system", "sleep", "Popen", "run"}
    check("observer_contains_no_write_control_or_sleep_calls", not (forbidden & set(calls)))
    started = time.perf_counter()
    cpu0 = time.process_time()
    with patch.object(Path, "write_text", side_effect=AssertionError("collect attempted write")), patch.object(Path, "write_bytes", side_effect=AssertionError("collect attempted write")):
        first = m.collect()
        second = m.collect(first)
    wall = time.perf_counter() - started
    cpu = time.process_time() - cpu0
    check("fixed_scope_exact_three_UUIDs", {x["uuid"] for x in second["objects"]} == {x["uuid"] for x in scope["objects"]})
    check("collect_static_positive_accepted", second["static_EP_comparison_baseline"]["accepted"] is True)
    check("signature_excludes_observation_UTC_ticks_registry_SHA", first["signature"] == second["signature"])
    check("completion_awaits_three_terminal_objects", second["completion"]["scope_object_count"] == 3 and not second["completion"]["all_fixed_objects_terminal"])
    payload = json.dumps(second, sort_keys=True, separators=(",", ":")).encode()
    check("payload_under_one_MiB_uncompressed_and_compressed", len(payload) < 1048576 and len(gzip.compress(payload)) < 1048576)
    return {"schema":"HISTORICAL_PROVIDER_CPU_QUALIFICATION_V2", "status":"ALL_PASS", "source_sha256":hashlib.sha256((HERE / "historical_provider.py").read_bytes()).hexdigest(), "scope_sha256":m.SCOPE_SHA256, "cases":cases, "two_collect_wall_seconds":wall, "two_collect_CPU_seconds":cpu, "payload_bytes":len(payload), "gzip_payload_bytes":len(gzip.compress(payload)), "production_daemon_started":False, "models_started":0, "controller_actions":0, "Git_READY_actions":0}, second


if __name__ == "__main__":
    qualification, sample = run()
    (HERE / "CPU_QUALIFICATION.json").write_text(json.dumps(qualification, indent=2) + "\n")
    (HERE / "QUALIFICATION_SAMPLE.json").write_text(json.dumps(sample, indent=2) + "\n")
    print(json.dumps(qualification, indent=2))
