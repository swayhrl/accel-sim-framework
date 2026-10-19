"""PREPARED_NOT_TESTED: pure supplied-bytes SEM1 result summary; no CLI or IO.

No process/filesystem/network/clock APIs. Parent must independently verify actual
published source, registration, ownership/resource/ABI evidence and pin every
input digest. Hash-consistent JSON alone cannot establish runtime provenance.
No native, ISA, architectural, application or coherence PASS can be returned.
"""
import hashlib
import json
import re
import types

MODES = ("shared", "masked", "with-e", "ae", "ad", "no-e",
         "wrong-byte", "missing-sector", "wrong-generation", "early-release")
POSITIVE = frozenset(MODES[:5])
NEGATIVE = frozenset(MODES[6:])
CLASSIFIER_SHA = "e58caa464124703d65e8d2bd88c6108a2376ef8a01c48b6db8e49273be5a0b61"
LIB = "/workspace/dtc-evidence-closure-20261019-v1/sem1/implementation-r1/build/libcudart.so"
ELF = "/workspace/dtc-evidence-closure-20261019-v1/sem1/implementation-r1/build/dtc_l1_sem1_values_ldst"
CONFIG = "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
IDENTITY = ("boot_id", "pid", "start_ticks", "tgid")
BYTE = re.compile(r"^SEM1_BYTE uid=(\d+) byte=(\d+) got=(\d+) expected=(\d+)$")
KEY = re.compile(r"^(entry/ENTRY_(START|TERMINAL)\.json|cohort/(MANAGER_(START|RESULT)|EMERGENCY_CLEANUP)\.json|cohort/cases/("
                 + "|".join(MODES) + r")/(START\.json|TERMINAL\.json|stdout\.log|stderr\.log|FINAL_RESOURCE\.json|RESOURCE_[0-9]{4}\.json|admission/(FIRST|SECOND|ADMISSION)\.json))$")


def require(value, why):
    if not value:
        raise ValueError(why)


def sha(value):
    require(type(value) is bytes, "EXACT_BYTES_REQUIRED")
    return hashlib.sha256(value).hexdigest()


def parse_json(value):
    require(type(value) is bytes and len(value) <= 2 * 1024**2, "BOUNDED_JSON_BYTES_REQUIRED")
    def pairs(items):
        result = {}
        for key, entry in items:
            require(key not in result, "DUPLICATE_JSON_KEY:" + key)
            result[key] = entry
        return result
    def no_constant(value):
        raise ValueError("NONFINITE_JSON_CONSTANT:" + value)
    return json.loads(value.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=no_constant)


def summarize(bundle, *, expected_file_sha256, expected_registration_sha256,
              expected_trusted_hashes, expected_output, classifier_source):
    """Caller supplies exact closed-file bytes and independently pinned hashes.

    bundle keys use entry/ENTRY_*.json and cohort/{MANAGER_*,cases/MODE/...}.
    No raw directory discovery or active-file access exists in this function.
    Returns protocol/evidence consistency only, never execution authorization.
    Partial receipts remain partial; missing modes are not fabricated as passes.
    """
    report = {"status": "SUPPLIED_RECEIPTS_INCOMPLETE_OR_REJECTED",
        "scope": "SUPPLIED_BYTES_ONLY_PARENT_ACTUAL_IMMUTABLE_BINDING_REQUIRED",
        "native": "UNPROVEN", "architectural_values": "UNPROVEN",
        "functional_ISA": "UNPROVEN", "coherence": "UNPROVEN",
        "application_equivalence": "UNPROVEN", "simulation_permission": False,
        "cases": [], "errors": [], "counts": {
            "architectural_production_value_tests": 0,
            "conditional_routing_positive_cases": 0,
            "conditional_no_E_countermodels": 0,
            "targeted_rejection_controls": 0,
            "standalone_structural_regression_suites": 0,
            "native_validations": 0},
        "all_ten_consistent": False}
    try:
        _summarize(report, bundle, expected_file_sha256,
                   expected_registration_sha256, expected_trusted_hashes,
                   expected_output, classifier_source)
    except (ValueError, KeyError, TypeError, UnicodeError, IndexError) as error:
        report["errors"].append(type(error).__name__ + ":" + str(error))
    return report


def _summarize(report, bundle, expected_files, expected_reg, trusted, output, classifier_source):
    require(type(bundle) is dict and bundle and set(bundle) == set(expected_files),
            "EXACT_PARENT_BOUND_FILE_POPULATION_REQUIRED")
    require(len(bundle) <= 4000 and all(type(value) is bytes for value in bundle.values())
            and sum(map(len, bundle.values())) <= 64 * 1024**2, "CLOSED_BUNDLE_64MiB_BOUND")
    require(all(KEY.fullmatch(key) and sha(value) == expected_files[key]
                for key, value in bundle.items()), "CLOSED_FILE_DIGEST_OR_SCOPE_CHANGED")
    require(isinstance(output, str) and output.startswith(
            "/workspace/dtc-evidence-closure-20261019-v1/sem1/fixture-runtime-v1/")
            and ".." not in output.split("/"), "PARENT_EXACT_OUTPUT_REQUIRED")
    require(sha(classifier_source) == CLASSIFIER_SHA, "UNCHANGED_CLASSIFIER_BYTES_REQUIRED")
    module = types.ModuleType("_sem1_exact_output_protocol")
    exec(compile(classifier_source, "<parent-bound-classifier>", "exec"), module.__dict__)
    def get(key):
        return parse_json(bundle[key])
    entry_start = get("entry/ENTRY_START.json")
    entry_terminal = get("entry/ENTRY_TERMINAL.json")
    manager_start = get("cohort/MANAGER_START.json")
    manager_result = get("cohort/MANAGER_RESULT.json")
    require(entry_start["registration_sha256"] == manager_start["registration_sha256"]
            == expected_reg and entry_start["trusted"] == manager_start["trusted"] == trusted,
            "ENTRY_MANAGER_INDEPENDENT_BINDING_MISMATCH")
    manager = manager_start["manager"]
    require(entry_start["pid"] == manager["pid"] and manager_start["total_seconds"] == 900
            and manager_start["concurrency"] == 1
            and manager_start["role"] == "SEM1_ACTUAL_OBJECT_FIXTURE_RUNTIME_V1",
            "ACTUAL_MANAGER_IDENTITY_OR_COHORT_SCOPE_CHANGED")
    require(entry_terminal["cohort_calls"] == 1 and entry_terminal["error"] is None
            and entry_terminal["report"] == manager_result,
            "OUTER_REPORT_NOT_THE_ONE_ACTUAL_COHORT")
    require(manager_result["simulation_starts"] == 0
            and manager_result["native"] == manager_result["architectural_values"] == "UNPROVEN",
            "SCIENTIFIC_BOUNDARY_CHANGED")
    prefix = manager_result["cases"]
    require([row["mode"] for row in prefix] == list(MODES[:len(prefix)])
            and len(prefix) <= 10, "FIXED_CASE_PREFIX_CHANGED")
    records = {row["mode"]: row for row in prefix}
    report["file_sha256"] = dict(expected_files)
    report["parent_registration_sha256"] = expected_reg
    report["reported_elapsed_seconds"] = manager_result["elapsed_seconds"]
    report["reported_cohort_status"] = manager_result["status"]
    report["reported_cohort_failure"] = manager_result["failure"]
    report["parent_reported_popen_returns"] = manager_result["actual_Popen_count"]
    report["actual_kernel_forks_independently_observed"] = "UNAVAILABLE_FROM_THESE_RECEIPTS"
    report["resource_scope"] = "SOURCE_BOUND_REPORTED_CHECKS_NOT_INDEPENDENT_OS_REEVALUATION"
    oom_baseline = [None]
    for mode in MODES:
        row = {"mode": mode, "status": "NOT_EXECUTED_OR_UNAVAILABLE",
               "native": "UNPROVEN", "architectural_values": "UNPROVEN"}
        if mode in records:
            try:
                _case(row, mode, records[mode], bundle, get, module, trusted,
                      manager, output, oom_baseline)
                field = ("conditional_routing_positive_cases" if mode in POSITIVE else
                         "conditional_no_E_countermodels" if mode == "no-e" else
                         "targeted_rejection_controls")
                report["counts"][field] += 1
            except (ValueError, KeyError, TypeError, UnicodeError, IndexError) as error:
                row.update(status="STOP_OR_UNRESOLVED_CASE",
                           reason=type(error).__name__ + ":" + str(error))
                report["errors"].append(mode + ":" + row["reason"])
        report["cases"].append(row)
    known_returns = sum(row.get("popen_returned") is True for row in prefix)
    require(manager_result["actual_Popen_count"] == known_returns, "REPORTED_POPEN_COUNT_CHANGED")
    if "cohort/EMERGENCY_CLEANUP.json" in bundle:
        report["errors"].append("EMERGENCY_CLEANUP_PRESENT_NO_COMPLETE_COHORT")
    complete = (len(prefix) == 10 and not report["errors"] and
                manager_result["failure"] is None and
                manager_result["status"] == "COMPLETE_CONDITIONAL_FIXTURE_COHORT_ONLY")
    report["all_ten_consistent"] = complete
    if complete:
        report["status"] = "TEN_CASE_SUPPLIED_RECEIPTS_CONSISTENT_CONDITIONAL_ONLY"


def _case(row, mode, recorded, bundle, get, classifier, trusted, manager, output, baseline):
    base = "cohort/cases/" + mode + "/"
    terminal = get(base + "TERMINAL.json")
    require(recorded == terminal and terminal["mode"] == mode, "CASE_RECORD_NOT_ACTUAL_TERMINAL_BYTES")
    require(terminal["popen_returned"] is True and terminal["reason"] is None
            and terminal["cleanup"]["reaped"] is True
            and not terminal["cleanup"].get("signals")
            and terminal["leftovers"] == [], "EXECUTION_OR_CLEANUP_FAILURE_OVERRIDES_EXPECTED_NEGATIVE")
    start = get(base + "START.json")
    child = start["instance"]
    require(start["actual_Popen"] is True and start["trusted"] == trusted
            and start["manager_instance"] == manager
            and all(child[key] == terminal["actual_instance"][key] for key in IDENTITY)
            and child["ppid"] == manager["pid"] and child["boot_id"] == manager["boot_id"]
            and child["pid"] == child["tgid"] == child["pgrp"] == child["session"],
            "ACTUAL_RETAINED_CHILD_IDENTITY_MISMATCH")
    require(start["argv"] == [ELF, CONFIG, mode] and start["cwd"] == output + "/cases/" + mode,
            "EXACT_SOURCE_BOUND_CASE_ARGV_CWD_REQUIRED")
    require(start["env"] == {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C",
            "CUDA_VISIBLE_DEVICES": "", "LD_LIBRARY_PATH": LIB.rsplit("/", 1)[0],
            "TMPDIR": output + "/cases/" + mode + "/tmp"}, "CLEAN_CASE_ENVIRONMENT_CHANGED")
    first, second = get(base + "admission/FIRST.json"), get(base + "admission/SECOND.json")
    admission = get(base + "admission/ADMISSION.json")
    require(admission["status"] == "PASS_CPU_ADMISSION_ONLY" and admission["checks"]
            and all(value is True for value in admission["checks"].values())
            and second["monotonic_ns"] - first["monotonic_ns"] >= 10 * 10**9,
            "FRESH_COMPLETE_CASE_ADMISSION_NOT_JOINED")
    resources = sorted(key for key in bundle if key.startswith(base)
                       and re.fullmatch(r"RESOURCE_[0-9]{4}\.json", key[len(base):]))
    require(resources, "NO_ACTUAL_RUNTIME_RESOURCE_RECEIPT")
    samples = [first, second]
    projections = 0
    for key in resources + [base + "FINAL_RESOURCE.json"]:
        item = get(key)
        require(item["checks"] and all(value is True for value in item["checks"].values()),
                "RESOURCE_FAILURE_OVERRIDES_NEGATIVE")
        samples.append(item["sample"])
    for sample in samples:
        require(sample["authority"]["status"] == "PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY"
                and sample["disk_free"] > 5 * 1024**3,
                "REPORTED_CURRENT_AUTHORITY_OR_DISK_NOT_PASS")
        events = (sample["host_oom_kill"], sample["cgroup_events"]["oom"],
                  sample["cgroup_events"]["oom_kill"])
        if baseline[0] is None:
            baseline[0] = events
        require(events == baseline[0], "REPORTED_COHORT_OOM_CHANGED")
        projections += len(sample["authority"].get("own_fixture_terminal_projection", []))
    require(terminal["live_observation"] in ("OBSERVED_CURRENT_DIRECT_CHILD", "UNAVAILABLE_NO_RETRY"),
            "UNKNOWN_LIVE_OBSERVATION_STATUS")
    last = terminal["last_actual_live_image"]
    if terminal["live_observation"] == "OBSERVED_CURRENT_DIRECT_CHILD":
        require(last is not None and all(last[key] == child[key] for key in IDENTITY)
                and last["argv"] == start["argv"] and last["cwd"] == start["cwd"]
                and last["exe"] == ELF, "REPORTED_LIVE_IMAGE_IDENTITY_NOT_JOINED")
    else:
        require(last is None, "UNAVAILABLE_OBSERVATION_HAS_INCONSISTENT_LIVE_IMAGE")
    stdout, stderr = bundle[base + "stdout.log"], bundle[base + "stderr.log"]
    verdict = classifier.classify(mode, terminal["returncode"], stdout, stderr,
                                  expected_library_path=LIB, execution_failure_reason=None)
    expected = ("CONDITIONAL_SECTOR_VALUES" if mode in POSITIVE else
                "CONDITIONAL_COUNTERMODEL" if mode == "no-e" else "EXPECTED_TARGETED_REJECTION")
    require(verdict["status"] == expected and terminal["classification"] == verdict
            and terminal["status"] == expected, "SOURCE_BOUND_EXPECTED_OUTPUT_MISMATCH")
    observations = [tuple(map(int, match.groups())) for line in stdout.decode("utf-8").splitlines()
                    if (match := BYTE.fullmatch(line))]
    row.update(status=expected, actual_child={key: child[key] for key in IDENTITY},
        live_observation=terminal["live_observation"],
        loaded_library_stdout=(verdict.get("loaded_library_stdout", "PRESENT")),
        printed_byte_records=len(observations),
        printed_consumer_UIDs=sorted({entry[0] for entry in observations}),
        printed_mismatches=[dict(uid=uid, byte=byte, got=got, expected=want)
                            for uid, byte, got, want in observations if got != want],
        conditional_byte_observations=[dict(uid=uid, byte=byte, got=got, expected=want)
                                       for uid, byte, got, want in observations],
        reported_resource_receipts=len(resources) + 1,
        own_terminal_projection_receipts=projections,
        source_assertions="BOUND_SOURCE_ENFORCES_NOT_INDEPENDENT_REGISTER_OR_EVENT_TELEMETRY")
