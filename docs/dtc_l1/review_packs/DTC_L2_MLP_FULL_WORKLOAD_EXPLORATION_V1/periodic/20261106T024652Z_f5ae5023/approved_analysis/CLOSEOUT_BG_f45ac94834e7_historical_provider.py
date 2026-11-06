"""Fixed-generation historical observer. collect() performs reads only; no sleeps or writes."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import time

SCOPE_SHA256 = "3a2e3b119e37829214637c02626b3c851ba4c03e4986168d40d4f40e8af8381e"
SCHEMA = "HISTORICAL_LONGTAIL_PROVIDER_V2"
HERE = Path(__file__).resolve().parent
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024
MAX_PAYLOAD_BYTES = 1024 * 1024


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _read(path, expected_sha=None):
    p = Path(path)
    if p.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("document exceeds read budget: " + str(p))
    data = p.read_bytes()
    if len(data) > MAX_DOCUMENT_BYTES:
        raise ValueError("document grew beyond read budget")
    digest = _digest(data)
    if expected_sha is not None and digest != expected_sha:
        raise ValueError("SHA mismatch: " + str(p))
    return json.loads(data), {"path": str(p), "sha256": digest, "bytes": len(data)}


def _optional(path):
    try:
        return _read(path)
    except FileNotFoundError:
        return None, None


def _pin_errors(pins):
    errors = []
    for pin in pins:
        try:
            _read_or_hash(pin)
        except (OSError, ValueError) as error:
            errors.append(str(error)[:240])
    return errors


def _read_or_hash(pin):
    p = Path(pin["path"])
    if p.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("pinned document exceeds read budget")
    data = p.read_bytes()
    if len(data) > MAX_DOCUMENT_BYTES or _digest(data) != pin["sha256"]:
        raise ValueError("pinned source mismatch: " + str(p))


def _process(spec, previous=None):
    result = {"pid": spec["pid"], "start_ticks": spec["start_ticks"],
              "boot_id": spec["boot_id"], "handle_state": "UNOBSERVED",
              "cpu_ticks": None, "cpu_ticks_delta": None,
              "cpu_progress_confirmed": False}
    try:
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        if boot != spec["boot_id"]:
            result["handle_state"] = "BOOT_CHANGED_NOT_FOLLOWED"
            return result
        p = Path("/proc") / str(spec["pid"])
        # Split after the last ')' so spaces in comm cannot shift stat fields.
        fields = (p / "stat").read_text().rsplit(")", 1)[1].split()
        start = int(fields[19])
        if start != spec["start_ticks"]:
            result["handle_state"] = "PID_REUSED_NOT_FOLLOWED"
            return result
        cwd = os.readlink(str(p / "cwd"))
        cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        if cwd != spec["output"] or "accel-sim.out" not in cmd or "strace " in cmd:
            result["handle_state"] = "HANDLE_IDENTITY_MISMATCH"
            return result
        ticks = int(fields[11]) + int(fields[12])
        state = fields[0]
        result.update(handle_state="SAME_GENERATION_LIVE" if state != "Z" else "ZOMBIE_AWAIT_TERMINAL",
                      process_state=state, cpu_ticks=ticks,
                      elapsed_seconds=float(Path("/proc/uptime").read_text().split()[0]) - start / os.sysconf("SC_CLK_TCK"))
        prev = previous.get("process", {}) if isinstance(previous, dict) else {}
        if (prev.get("pid"), prev.get("start_ticks"), prev.get("boot_id")) == (spec["pid"], start, boot) and isinstance(prev.get("cpu_ticks"), int):
            delta = ticks - prev["cpu_ticks"]
            result["cpu_ticks_delta"] = delta if delta >= 0 else None
            result["cpu_progress_confirmed"] = delta > 0
    except FileNotFoundError:
        result["handle_state"] = "HANDLE_MISSING_NOT_TERMINAL"
    except (OSError, ValueError, IndexError) as error:
        result["handle_state"] = "HANDLE_UNREADABLE_NOT_TERMINAL"
        result["error"] = str(error)[:200]
    return result


def _same_identity(document, spec, require_input=False):
    if not isinstance(document, dict):
        return False
    if document.get("cohort") != spec["cohort"] or document.get("uuid") != spec["uuid"]:
        return False
    if document.get("source_identity") != spec["source_identity"]:
        return False
    if require_input and document.get("input_identity_sha256") != spec["input_identity_sha256"]:
        return False
    return True


def _link(link, actual, path):
    return (isinstance(link, dict) and actual is not None
            and link.get("path") == str(path) and link.get("sha256") == actual["sha256"])


def _terminal(spec, row, documents):
    """Pure decision function; missing/contradictory evidence never invents termination."""
    result = {"status": "HOLD_NO_OWN_TERMINAL_PROOF", "terminal": False,
              "accepted": False, "cycles": None, "reason": "No coherent terminal proof for fixed UUID."}
    if not isinstance(row, dict) or row.get("uuid") != spec["uuid"] or row.get("output") != spec["output"]:
        result["reason"] = "Registry fixed UUID/output mismatch or unavailable."
        return result
    done, dr = documents.get("done", (None, None))
    exit_doc, er = documents.get("exit", (None, None))
    point, pr = documents.get("point", (None, None))
    own_done = _same_identity(done, spec) and _same_identity(exit_doc, spec)
    if not own_done or not _link(row.get("done_ref"), dr, spec["done_path"]):
        result["reason"] = "Own DONE/EXIT identity or registry DONE SHA not yet coherent."
        return result
    for d in [done, exit_doc]:
        if d.get("spec_ref", {}).get("sha256") != spec["spec_sha256"]:
            result["reason"] = "Terminal spec SHA mismatch."
            return result
    metadata_pin = next(x for x in spec["pins"] if x["path"].endswith("/NATIVE_SIMULATOR_PID_AND_MAPS.json"))
    for d in [done, exit_doc]:
        closed_meta = d.get("closed_artifact_refs", {}).get("NATIVE_SIMULATOR_PID_AND_MAPS.json", {})
        if closed_meta.get("sha256") != metadata_pin["sha256"] or closed_meta.get("path") != metadata_pin["path"]:
            result["reason"] = "DONE/EXIT does not bind the pinned observed PID generation metadata."
            return result
    same_exit = (done.get("launcher_wait_returncode") == exit_doc.get("launcher_wait_returncode")
                 and done.get("stop_reason") == exit_doc.get("stop_reason"))
    if not same_exit:
        result["reason"] = "DONE/EXIT outcomes disagree."
        return result
    rc = done.get("launcher_wait_returncode")
    negative = ((isinstance(rc, int) and not isinstance(rc, bool) and rc != 0)
                or done.get("stop_reason") not in [None, ""])
    if negative and _same_identity(point, spec, True) and point.get("status") == "EP_FULL_PERF_APPLICATION_ACCEPTED":
        result.update(status="HOLD_TERMINAL_OUTCOME_CONFLICT", reason="Positive accepted point conflicts with negative native DONE/EXIT.")
        return result
    if negative:
        result.update(status="EXPLICIT_UNACCEPTED", terminal=True,
                      reason="Own coherent DONE/EXIT explicitly reports negative outcome.",
                      launcher_wait_returncode=rc, stop_reason=done.get("stop_reason"))
        return result
    archive_doc, archive_ref = documents.get("archive", (None, None))
    archived_negative = (row.get("state") == "CLOSED_UNACCEPTED" and isinstance(archive_doc, dict)
                         and archive_doc.get("cohort") == spec["cohort"] and archive_doc.get("uuid") == spec["uuid"]
                         and archive_doc.get("status") == "TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS"
                         and _link(row.get("archive_receipt_ref"), archive_ref, Path(spec["case_control"]) / "ARCHIVE_RECEIPT.json"))
    if archived_negative and point is None:
        result.update(status="EXPLICIT_UNACCEPTED", terminal=True,
                      reason="Own DONE/EXIT with exact registry CLOSED_UNACCEPTED and closed archive receipt; no accepted point.")
        return result
    if rc != 0 or done.get("native_simulator_observed") is not True:
        result["reason"] = "Successful native terminal receipt unavailable."
        return result
    result.update(status="HOLD_DONE_PENDING_STRICT_ACCEPTANCE",
                  reason="Native DONE exists; mandatory accepted/validation/archive closure pending.")
    if row.get("state") != "CLOSED_ACCEPTED" or not _same_identity(point, spec, True):
        return result
    if point.get("status") != "EP_FULL_PERF_APPLICATION_ACCEPTED" or point.get("hardware_drained") is not True:
        return result
    root = Path(spec["output"])
    bundle, br = documents.get("bundle", (None, None))
    archive, ar = documents.get("archive", (None, None))
    if not all([_link(row.get("accepted_point_ref"), pr, root / "ACCEPTED_POINT.json"),
                _link(row.get("validation_ref"), br, root / "VALIDATED_APPLICATION_BUNDLE.json"),
                _link(row.get("archive_receipt_ref"), ar, Path(spec["case_control"]) / "ARCHIVE_RECEIPT.json"),
                _link(point.get("done_ref"), dr, spec["done_path"]),
                _link(point.get("validation_ref"), br, root / "VALIDATED_APPLICATION_BUNDLE.json")]):
        return result
    if point.get("spec_ref", {}).get("sha256") != spec["spec_sha256"]:
        return result
    if not isinstance(bundle, dict) or bundle.get("cohort") != spec["cohort"] or bundle.get("source_identity") != spec["source_identity"] or bundle.get("input_identity_sha256") != spec["input_identity_sha256"] or bundle.get("hardware_drained") is not True:
        return result
    app = bundle.get("application", {})
    if app.get("actual_options") != spec["expected_effective_options"]:
        return result
    expected = {"CTA": spec["expected_CTA"], "instructions": spec["expected_instructions"], "kernel_count": len(spec["expected_kernel_launches"]) if isinstance(spec["expected_kernel_launches"], list) else spec["expected_kernel_launches"]}
    if any(point.get(k) != v or bundle.get(k) != v or app.get(k) != v for k, v in expected.items()):
        return result
    cycles = point.get("cycles")
    if not isinstance(cycles, int) or isinstance(cycles, bool) or cycles <= 0 or bundle.get("cycles") != cycles or app.get("cycles") != cycles:
        return result
    stream = point.get("raw_stream_receipt", {})
    if stream.get("complete_compressed_stream") is not True or stream.get("truncated") is not False:
        return result
    if not isinstance(archive, dict) or archive.get("uuid") != spec["uuid"] or archive.get("cohort") != spec["cohort"] or archive.get("status") != "TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS":
        return result
    restores = archive.get("native_restores", [])
    if len(restores) != 2 or not all(x.get("status") == "INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS" for x in restores):
        return result
    if {x.get("restore_label") for x in restores} != {"FIRST", "INDEPENDENT"} or not all(x.get("archive_sha256") == archive.get("archive_ref", {}).get("sha256") for x in restores):
        return result
    result.update(status="STRICT_ACCEPTED", terminal=True, accepted=True, cycles=cycles,
                  numeric_output=point.get("numeric_output"),
                  reason="Exact fixed UUID/input/source/spec/work/options plus existing accepted and archive/restore receipts coherent.")
    return result


def _object(spec, row, previous=None, observe_process=True):
    result = {k: spec[k] for k in ["cohort", "uuid", "input_identity_sha256", "source_identity", "mode", "program", "profile", "clock", "scientific_scope", "ordered_configs"]}
    result["configuration_contract_sha256"] = _digest(_canonical(spec["expected_effective_options"]))
    result["role"] = "EP_FIXED_HISTORICAL_UUID"
    process = _process(spec, previous) if observe_process else {"handle_state": "STATIC_COMPARISON_BASELINE_NO_PROCESS_FOLLOW"}
    result["process"] = process
    errors = _pin_errors(spec["pins"])
    result["contract_errors"] = errors
    result.update(status="HOLD_CONTRACT_UNVERIFIED", terminal=False, accepted=False, cycles=None)
    if errors:
        return result
    root = Path(spec["output"])
    paths = {"done": Path(spec["done_path"]), "exit": root / "NATIVE_EXIT.json",
             "point": root / "ACCEPTED_POINT.json", "bundle": root / "VALIDATED_APPLICATION_BUNDLE.json",
             "archive": Path(spec["case_control"]) / "ARCHIVE_RECEIPT.json"}
    documents = {k: _optional(p) for k, p in paths.items()}
    result.update(_terminal(spec, row, documents))
    result["evidence"] = {k: ref for k, (_, ref) in documents.items() if ref is not None}
    live = process["handle_state"] == "SAME_GENERATION_LIVE"
    if live:
        if result["terminal"]:
            result.update(status="HOLD_LIVE_TERMINAL_CONFLICT", terminal=False, accepted=False, cycles=None,
                          reason="Fixed live generation conflicts with terminal documents.")
        else:
            result.update(status="LIVE_CPU_PROGRESS" if process["cpu_progress_confirmed"] else "LIVE_SAME_GENERATION",
                          reason="Fixed PID/start/boot/output observed. A single unchanged sample is not stalled/terminal proof.")
    try:
        raw = root / "raw.log.gz"
        result["progress"] = {"initial_snapshot_telemetry_cycle": spec.get("initial_telemetry_cycle"),
                              "raw_compressed_bytes": raw.stat().st_size,
                              "accepted_fraction": None, "eta_seconds": None}
    except OSError:
        result["progress"] = {"eta_seconds": None, "accepted_fraction": None}
    return result


def _comparison(current, baseline, spec, baseline_spec):
    answer = {"baseline_uuid": baseline_spec["uuid"], "baseline_mode": baseline_spec["mode"],
              "cycles_over_baseline": None, "baseline_cycles_over_cycles": None,
              "policy": "Explicit same-input/source/work EP pair only; no GM; no DTC merge."}
    answer["configuration_changes_from_baseline"] = {k: {"baseline": baseline_spec["expected_effective_options"].get(k), "current": spec["expected_effective_options"].get(k)} for k in sorted(set(spec["expected_effective_options"]) | set(baseline_spec["expected_effective_options"])) if spec["expected_effective_options"].get(k) != baseline_spec["expected_effective_options"].get(k)}
    keys = ["input_identity_sha256", "source_identity", "expected_CTA", "expected_instructions", "expected_kernel_launches", "clock"]
    if not all(spec.get(k) == baseline_spec.get(k) for k in keys):
        answer["status"] = "HOLD_BASELINE_CONTRACT_NOT_MATCHED"
    elif current.get("accepted") and baseline.get("accepted"):
        answer.update(status="MATCHED_STRICT_ACCEPTED_PAIR", cycles_over_baseline=current["cycles"] / baseline["cycles"],
                      baseline_cycles_over_cycles=baseline["cycles"] / current["cycles"], baseline_cycles=baseline["cycles"])
    else:
        answer["status"] = "HOLD_AWAIT_BOTH_STRICT_ACCEPTED"
    return answer


def collect(previous=None):
    """Return a JSON-serializable snapshot. Caller owns persistence and scheduling."""
    observed = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = {"schema": SCHEMA, "observed_utc": observed, "scope_sha256": SCOPE_SHA256,
              "role": "HISTORICAL_REPORT_ONLY", "objects": [],
              "completion": {"scope_object_count": 3, "terminal_object_count": 0, "all_fixed_objects_terminal": False},
              "read_only": True, "eta_seconds": None}
    try:
        scope, sr = _read(HERE / "SCOPE.json", SCOPE_SHA256)
        baseline, bref = _read(scope["baseline_ref"]["path"], scope["baseline_ref"]["sha256"])
        errors = _pin_errors(baseline["source_pins"])
        result["downstream18"] = {"status": "IMMUTABLE_BASELINE_SHA_VERIFIED" if not errors else "HOLD_BASELINE_SOURCE_SHA_CHANGED",
                                  "baseline_ref": bref, "source_errors": errors,
                                  "P0_equals_1_table": baseline["rows"] if not errors else [],
                                  "profile_differences": baseline["profile_differences"], "normalization": baseline["normalization"]}
        registry, regref = _read(scope["registry_path"])
        consumed = registry.get("registered_future_requests", {}).get(scope["request_id"], {}).get("consumed", {})
        result["registry_read_ref"] = regref
        prev = {x.get("uuid"): x for x in previous.get("objects", []) if isinstance(x, dict)} if isinstance(previous, dict) and previous.get("scope_sha256") == SCOPE_SHA256 else {}
        for spec in scope["objects"]:
            try:
                result["objects"].append(_object(spec, consumed.get(spec["cohort"]), prev.get(spec["uuid"])))
            except (OSError, ValueError, KeyError, TypeError) as error:
                result["objects"].append({"cohort": spec["cohort"], "uuid": spec["uuid"], "status": "HOLD_READ_OR_SCHEMA_ERROR", "terminal": False, "accepted": False, "cycles": None, "error": str(error)[:240]})
        bs = scope["static_comparison_baseline"]
        try:
            static = _object(bs, consumed.get(bs["cohort"]), observe_process=False)
        except (OSError, ValueError, KeyError, TypeError) as error:
            static = {"uuid": bs["uuid"], "accepted": False, "status": "HOLD_BASELINE_READ_ERROR", "error": str(error)[:240]}
        result["static_EP_comparison_baseline"] = static
        byr = {x["cohort"]: x for x in result["objects"]}
        for spec, row in zip(scope["objects"], result["objects"]):
            if spec["program"].upper() == "SYRK":
                bspec = scope["objects"][0]
                brow = byr.get(bspec["cohort"], {})
            else:
                bspec, brow = bs, static
            row["baseline_comparison"] = _comparison(row, brow, spec, bspec)
        result["old_v100_static_note"] = scope["old_v100_static_note"]
        result["historical_v1_report_ref"] = scope["v1_report_ref"]
        n = sum(x.get("terminal") is True for x in result["objects"])
        result["completion"].update(terminal_object_count=n, all_fixed_objects_terminal=len(result["objects"]) == 3 and n == 3)
        result["status"] = "FIXED_SCOPE_TERMINAL" if n == 3 else "OBSERVING_FIXED_SCOPE"
    except (OSError, ValueError, KeyError, TypeError) as error:
        result.update(status="HOLD_PROVIDER_SOURCE_OR_REGISTRY_UNAVAILABLE", error=str(error)[:300])
    scientific = {"scope_sha256": SCOPE_SHA256, "status": result.get("status"),
                  "downstream18_status": result.get("downstream18", {}).get("status"),
                  "objects": [{k: x.get(k) for k in ["uuid", "status", "terminal", "accepted", "cycles", "input_identity_sha256", "source_identity", "baseline_comparison"]} for x in result["objects"]]}
    # Liveness may toggle CPU_PROGRESS without a scientific transition.
    for obj in scientific["objects"]:
        if obj["status"] in ["LIVE_CPU_PROGRESS", "LIVE_SAME_GENERATION"]:
            obj["status"] = "LIVE_SAME_GENERATION"
    result["signature"] = _digest(_canonical(scientific))
    size = len(_canonical(result))
    if size > MAX_PAYLOAD_BYTES:
        return {"schema": SCHEMA, "observed_utc": observed, "scope_sha256": SCOPE_SHA256,
                "status": "HOLD_PAYLOAD_BUDGET", "payload_bytes": size, "objects": [],
                "completion": {"scope_object_count": 3, "terminal_object_count": 0, "all_fixed_objects_terminal": False},
                "read_only": True, "signature": _digest(_canonical({"scope": SCOPE_SHA256, "status": "HOLD_PAYLOAD_BUDGET"}))}
    result["payload_bytes_before_size_field"] = size
    return result


if __name__ == "__main__":
    print(json.dumps(collect(), sort_keys=True, separators=(",", ":")))
