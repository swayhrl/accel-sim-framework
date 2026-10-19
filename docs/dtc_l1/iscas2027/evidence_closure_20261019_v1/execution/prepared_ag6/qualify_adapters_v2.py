"""SOURCE_PREPARED_NOT_EXECUTED: parent-only AG6 CPU adapter qualification.

Copy unchanged to parent's prepared_ag6, then freeze/register/publish there.
No target Popen, ptrace, external signal, new fixture root or simulator API.
Only fixed read-only Git commands may create tooling children. Own SIGALRM
bounds this foreground Python; payload imports occur after fresh CPU admission.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
EX = HERE.parent
FW = HERE.parents[5]
ENGINE = EX / "prepared_runtime"
COHORT = Path("/workspace/dtc-evidence-closure-20261019-v1/coordinator/ag6-v2")
OUTPUT = COHORT / "cpu-adapter-qualification-v2"
PUBLICATION = COHORT / "cpu-adapter-qualification-v2-prereg/PUBLICATION_READBACK.json"
REGISTRATION = EX / "AG6_CPU_ADAPTER_REGISTRATION_V2.json"
BRANCH = "hrl/iscas2027-dtc-closure-exec-174-v1"
READBACK = "refs/dtc-closure-readback/ag6-cpu-adapters-v2"
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
TIMEOUT = 90
OUTPUT_BOUND = 1024**2
ROOT_BASE = Path("/workspace/dtc-evidence-closure-20261019-v1/coordinator/cpu-qualification/ag5-integrated-v2")
ROOTS = (ROOT_BASE / "root0", ROOT_BASE / "root1")
ROOT_FILES = ("TERMINAL.json", "START.json", "CHILD.json", "FORK_CHILD.json", "MAP_EVENTS.jsonl")
PARSER_INPUTS = {
    "preregistration": EX / "AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json",
    "science_manifest": EX / "ag6_final_prep_intake/AG6_FOUR_ARM_SCIENCE_PROPOSAL.json",
    "kernel_audit": HERE / "identity_metadata/KERNEL_BODY_AUDIT.tsv",
    "metric_dictionary": EX / "ag6_final_prep_intake/FROZEN_METRIC_DICTIONARY.tsv",
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def canonical_sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            result.update(block)
    return result.hexdigest()


def metadata(descriptor):
    path = Path(descriptor["path"])
    require(path.is_absolute() and path.stat().st_size <= 2 * 1024**2,
            "BOUNDED_ABSOLUTE_METADATA_REQUIRED")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == descriptor["sha256"],
            "REGISTERED_METADATA_CHANGED:" + str(path))
    return data


def git(deadline, *arguments):
    remaining = deadline - time.monotonic()
    require(remaining > 0, "ADAPTER_TOTAL_BOUND")
    return subprocess.check_output(["/usr/bin/git", "--no-optional-locks", "-C", str(FW),
        "-c", "core.fsmonitor=false", *arguments], env=ENV, text=True,
        timeout=remaining).strip()


def publication(deadline):
    receipt = json.loads(PUBLICATION.read_bytes())
    head, tree = receipt["head"], receipt["tree"]
    require(receipt["fetched_head"] == head and receipt["fetched_tree"] == tree and
            receipt["branch"] == BRANCH, "EXACT_PUBLICATION_READBACK_REQUIRED")
    require(git(deadline, "rev-parse", "HEAD") == head == git(deadline, "rev-parse", READBACK) and
            git(deadline, "rev-parse", "HEAD^{tree}") == tree ==
            git(deadline, "rev-parse", READBACK + "^{tree}"), "CLEAN_HEAD_TREE_READBACK_MISMATCH")
    require(not git(deadline, "status", "--porcelain"), "CLEAN_REGISTERED_SOURCE_REQUIRED")
    remote = git(deadline, "ls-remote", "--exit-code", "origin", "refs/heads/" + BRANCH).splitlines()
    require(remote == [head + "\trefs/heads/" + BRANCH], "REMOTE_EXACT_BRANCH_HEAD_CHANGED")
    for relative, binding in receipt["files"].items():
        path = (FW / relative).resolve()
        require(path.is_relative_to(FW) and sha(path) == binding["sha256"] and
                git(deadline, "rev-parse", head + ":" + relative) == binding["blob"],
                "PUBLISHED_SOURCE_OR_BLOB_CHANGED:" + relative)
    require(str(REGISTRATION.relative_to(FW)) in receipt["files"], "REGISTRATION_NOT_PUBLISHED")
    registration = json.loads(REGISTRATION.read_bytes())
    required = [HERE / name for name in ("qualify_adapters_v2.py", "ag6_strict.py",
                "targeted_qualification.py", "ag6_input_runtime_identity.py", "close_attempt_v2.py")]
    required += [ENGINE / "cpu_admission_v2.py", ENGINE / "shared_authority.py", ENGINE / "vendor/ownership.py"]
    sources = registration["source_sha256"]
    require(set(map(str, required)) <= set(sources), "EXACT_ADAPTER_AND_GATE_IMPORT_CLOSURE_REQUIRED")
    require(len(canonical(sources)) <= 64 * 1024, "COMPACT_SOURCE_BINDING_REQUIRED")
    for absolute, expected in sources.items():
        path = Path(absolute).resolve()
        require(path.is_relative_to(FW), "REGISTERED_IMPORT_SOURCE_OUTSIDE_FROZEN_FRAMEWORK")
        relative = str(path.relative_to(FW))
        require(relative in receipt["files"] and receipt["files"][relative]["sha256"] == expected and
                sha(path) == expected, "SOURCE_HASH_NOT_IN_REMOTE_PUBLICATION:" + absolute)
    require(registration["status"] == "REGISTERED_FOR_AG6_CPU_ADAPTER_QUALIFICATION_ONLY" and
            registration["timeout_seconds"] == TIMEOUT and registration["output_bound_bytes"] == OUTPUT_BOUND and
            registration["output"] == str(OUTPUT) and registration["new_target_roots"] == 0 and
            registration["simulation_starts"] == 0 and
            registration["admission"]["disk_floor_exclusive_bytes"] == 5 * 1024**3,
            "FIXED_90S_1MIB_CPU_ONLY_5G_REGISTRATION_REQUIRED")
    roles = registration["gate_roles"]
    require(len(roles) == 1 and roles[0]["name"] == "AG6_CPU_ADAPTER_QUALIFICATION_V2" and
            roles[0]["argvs"] == [["/usr/bin/python3.10", "-I", "-B", str(HERE / "qualify_adapters_v2.py")]] and
            roles[0]["cwd"] == str(FW) and roles[0]["executable"] == "/usr/bin/python3.10" and
            sha(roles[0]["executable"]) == roles[0]["executable_sha256"] and
            roles[0]["source_sha256"] == sources, "SOURCE_BOUND_SELF_ROLE_REQUIRED")
    return registration, receipt


def module_binding(module, path, sources):
    require(Path(module.__file__).resolve() == path.resolve() and sha(path) == sources[str(path)],
            "ACTUAL_IMPORTED_MODULE_OR_SOURCE_CHANGED:" + str(path))


def reuse_inputs(registration, published):
    descriptor = registration["closed_CPU_mapping_inputs"]
    shared = json.loads(metadata(descriptor["shared_PASS"]))
    original = json.loads(metadata(descriptor["source_registration"]))
    for name in ("shared_PASS", "source_registration"):
        path = Path(descriptor[name]["path"]).resolve()
        require(path.is_relative_to(FW), "PUBLISHED_SHARED_RECEIPT_COPY_REQUIRED")
        relative = str(path.relative_to(FW))
        require(relative in published["files"] and
                published["files"][relative]["sha256"] == descriptor[name]["sha256"],
                "SHARED_PROOF_NOT_IN_EXACT_PUBLICATION")
    require(shared["status"] == "PASS_TWO_REAL_ROOTS_SHARED_OBSERVER_CPU_ONLY" and
            shared["simulation_starts"] == 0 and bool(shared["checks"]) and
            all(value is True for value in shared["checks"].values()) and
            shared["registration_sha256"] == descriptor["source_registration"]["sha256"] and
            shared["prepared_source_sha256"] == original["prepared_source_sha256"] and
            len(shared["prepared_source_sha256"]) == 39,
            "ACTUAL_SHARED_PASS_SOURCE_REGISTRATION_JOIN_REQUIRED")
    require(len(original["requests"]) == len(descriptor["roots"]) == len(shared["evidence"]) == 2 and
            tuple(row["destination"] for row in original["requests"]) == tuple(map(str, ROOTS)) and
            tuple(row["path"] for row in descriptor["roots"]) == tuple(map(str, ROOTS)),
            "ONLY_TWO_ALREADY_CLOSED_REGISTERED_CPU_ROOTS")
    manifest_bytes = metadata(descriptor["CPU_manifest"])
    manifest_sha = descriptor["CPU_manifest"]["sha256"]
    require(shared["manifests_sha256"] == manifest_sha and all(
        row["manifests_path"] == descriptor["CPU_manifest"]["path"] and
        row["manifests_sha256"] == manifest_sha for row in original["requests"]),
        "ACTUAL_CPU_MANIFEST_SOURCE_BINDING_REQUIRED")
    return descriptor, shared, json.loads(manifest_bytes)


def verify_root_files(descriptor):
    root = Path(descriptor["path"])
    require(root in ROOTS and set(descriptor["receipt_sha256"]) == set(ROOT_FILES),
            "ALL_FIVE_EXACT_CLOSED_ROOT_RECEIPTS_REQUIRED")
    for name in ROOT_FILES:
        require(sha(root / name) == descriptor["receipt_sha256"][name], "CLOSED_ROOT_RECEIPT_CHANGED:" + name)
    terminal = json.loads((root / "TERMINAL.json").read_bytes())
    child = json.loads((root / "CHILD.json").read_bytes())
    require(terminal["status"] == "PASS_GUARDED_NATURAL_EXIT0" and terminal["purpose"] == "CPU_FIXTURE" and
            terminal["returncode"] == 0 and terminal["forced_reason"] is None and
            terminal["exception"] is None and terminal["identity_pass"] is True and
            terminal["simulator_starts"] == 0 and terminal["owned_children_live"] == 0 and
            not terminal["ownership"]["confirmed"] and not terminal["ownership"]["pending"] and
            not terminal["unconfirmed_wait_pids"] and len(terminal["owned_process_exit_instances"]) == 58 and
            terminal["snapshots"] == 1882, "ACTUAL_CLOSED_58_INSTANCE_1882_MAP_CPU_ROOT_REQUIRED")
    require(child["actual_fork"] is True and child["real_simulator"] is False,
            "NO_SIMULATION_OR_FABRICATED_ROOT")
    return child


def main():
    require(sys.argv == [str(HERE / "qualify_adapters_v2.py")] and dict(os.environ) == ENV and
            HERE.name == "prepared_ag6" and Path.cwd() == FW and sys.flags.isolated and
            sys.flags.dont_write_bytecode, "EXACT_PARENT_FOREGROUND_ENTRY_AND_CLEAN_ENV_REQUIRED")
    require(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0), "MUST_NOT_REPLACE_ACTIVE_TIMER")
    prior_handler = signal.getsignal(signal.SIGALRM)
    def own_timeout(number, frame):
        raise TimeoutError("AG6_CPU_ADAPTER_90S_TOTAL_BOUND")
    signal.signal(signal.SIGALRM, own_timeout)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
    began = time.monotonic()
    deadline = began + TIMEOUT
    written = 0
    def write(name, value):
        nonlocal written
        data = canonical(value) + b"\n"
        # Retain room for a compact terminal even after a failed intermediate
        # receipt bound. Admission's unchanged FIRST/SECOND files are separate.
        bound = OUTPUT_BOUND if name == "ENTRY_TERMINAL.json" else OUTPUT_BOUND - 128 * 1024
        require(written + len(data) <= bound, "COMPACT_OUTPUT_PAYLOAD_BOUND")
        with (OUTPUT / name).open("xb") as stream:
            stream.write(data)
        written += len(data)
    def checkpoint():
        require(time.monotonic() < deadline, "ADAPTER_TOTAL_BOUND")
    report = dict(status="STOP_AG6_CPU_ADAPTER_QUALIFICATION", parser_cases_executed=0,
                  actual_identity_calls=0, existing_CPU_mapping_calls=0,
                  new_target_roots=0, simulation_starts=0, no_retry=True)
    created = False
    try:
        OUTPUT.mkdir(parents=True, exist_ok=False)
        created = True
        write("ENTRY_START.json", dict(utc=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
            argv=sys.argv, cwd=str(FW), timeout_seconds=TIMEOUT, output_bound_bytes=OUTPUT_BOUND,
            scope="CPU_ADAPTER_QUALIFICATION_ONLY_NOT_AG6_EXECUTION"))
        registration, published = publication(deadline)
        binding = dict(registration_sha256=sha(REGISTRATION), publication_sha256=sha(PUBLICATION),
                       publication_head=published["head"], publication_tree=published["tree"],
                       prepared_source_sha256=registration["source_sha256"])
        report.update(binding)
        write("SOURCE_PUBLICATION_BINDING.json", dict(binding, remote_branch=BRANCH,
              readback_ref=READBACK, clean=True, published_file_count=len(published["files"])))
        # Only necessary source-bound gate imports precede fresh R2.
        sys.path.insert(0, str(ENGINE / "vendor"))
        sys.path.insert(0, str(ENGINE))
        from cpu_admission_v2 import CPUAdmission
        import cpu_admission_v2
        module_binding(cpu_admission_v2, ENGINE / "cpu_admission_v2.py", registration["source_sha256"])
        if not CPUAdmission(registration, registration["gate_roles"]).admit(OUTPUT / "admission"):
            report["status"] = "WAIT_RESOURCE_OR_AUTHORITY_ZERO_ADAPTER_WORK"
        else:
            report["admission_sha256"] = sha(OUTPUT / "admission/ADMISSION.json")
            registration_again, published_again = publication(deadline)
            require(registration_again == registration and published_again == published,
                    "PUBLICATION_CHANGED_AFTER_FRESH_ADMISSION")
            sys.path.insert(0, str(HERE))
            import ag6_strict
            import targeted_qualification
            import ag6_input_runtime_identity
            import close_attempt_v2
            for module in (ag6_strict, targeted_qualification, ag6_input_runtime_identity, close_attempt_v2):
                module_binding(module, HERE / (module.__name__ + ".py"), registration["source_sha256"])
            checkpoint()
            descriptors = registration["parser_inputs"]
            require(set(descriptors) == set(PARSER_INPUTS) and all(
                descriptors[key]["path"] == str(path) for key, path in PARSER_INPUTS.items()),
                "EXACT_FROZEN_PARSER_METADATA_PATHS_REQUIRED")
            inputs = {key: metadata(value) for key, value in descriptors.items()}
            parser_report = targeted_qualification.qualify_targeted(ag6_strict,
                parser_source=(HERE / "ag6_strict.py").read_bytes(), **inputs)
            report["parser_cases_executed"] = parser_report["actual_case_count"]
            write("PARSER_TARGETED.json", parser_report)
            require(parser_report["status"] == "PASS_FOUR_DECLARED_SYNTHETIC_INTERFACE_CASES_ONLY" and
                    parser_report["actual_case_count"] == 4, "FOUR_TARGETED_PARSER_CASES_REQUIRED")
            checkpoint()
            report["actual_identity_calls"] = 1
            identity = ag6_input_runtime_identity.validate_identity(registration["identity_binding"], "AE_GEMM")
            require(identity["status"] == "PASS_PRELAUNCH_IDENTITY_ONLY" and
                    identity["trace_members_stat_checked"] == 511 and identity["source_files_sha_checked"] == 702 and
                    len(identity["runtime_files"]) == 12 and identity["trace_body_bytes_read"] == 0 and
                    identity["simulator_starts"] == 0, "BOUNDED_ACTUAL_PRELAUNCH_IDENTITY_REQUIRED")
            write("PRELAUNCH_IDENTITY.json", identity)
            checkpoint()
            descriptor, shared, mappings = reuse_inputs(registration, published)
            summaries = []
            for index, root_descriptor in enumerate(descriptor["roots"]):
                checkpoint()
                child = verify_root_files(root_descriptor)
                evidence = shared["evidence"][index]
                require(all(child[key] == evidence["root"][key] for key in ("pid", "start_ticks")) and
                        root_descriptor["receipt_sha256"]["MAP_EVENTS.jsonl"] == evidence["map_events_sha256"],
                        "SHARED_PASS_TO_CURRENT_CLOSED_ROOT_JOIN")
                report["existing_CPU_mapping_calls"] += 1
                result = close_attempt_v2.close_mapping(Path(root_descriptor["path"]), mappings, purpose="CPU_FIXTURE")
                payload_index = result.pop("map_payload_index")
                require(result["status"] == "PASS_ACTUAL_CLOSED_GUARD_EVENT_MAPPING_EXIT_JOIN" and
                        result["exit_instances"] == 58 and result["map_payloads"] == len(payload_index) == 1882 and
                        result["map_events_sha256"] == evidence["map_events_sha256"],
                        "ACTUAL_SHARED_CPU_POSTCLOSE_POPULATION_REQUIRED")
                result.update(root=root_descriptor["path"], purpose="CPU_FIXTURE",
                    map_payload_index_canonical_sha256=canonical_sha(payload_index),
                    map_payload_index_canonicalization="SORT_KEYS_COMPACT_JSON_ENSURE_ASCII_UTF8",
                    map_payload_index_written=False,
                    shared_PASS_sha256=descriptor["shared_PASS"]["sha256"],
                    source_registration_sha256=descriptor["source_registration"]["sha256"],
                    CPU_manifest_sha256=descriptor["CPU_manifest"]["sha256"],
                    closed_root_receipt_sha256=root_descriptor["receipt_sha256"])
                del payload_index
                verify_root_files(root_descriptor)
                summaries.append(result)
                write("CPU_MAPPING_ROOT" + str(index) + ".json", result)
            checkpoint()
            require(metadata(descriptor["shared_PASS"]) and metadata(descriptor["source_registration"])
                    and metadata(descriptor["CPU_manifest"]), "REUSE_PROVENANCE_POSTCHECK")
            final_registration, final_publication = publication(deadline)
            require(final_registration == registration and final_publication == published,
                    "SOURCE_OR_PUBLICATION_CHANGED_BEFORE_TERMINAL")
            report.update(status="PASS_AG6_CPU_ADAPTER_INTERFACES_ONLY", mapping_summaries=summaries,
                synthetic_parser_scope=True, identity_scope="PRELAUNCH_ONLY_NO_TRACE_BODY",
                mapping_scope="ALREADY_CLOSED_SHARED_CPU_FIXTURES_ONLY", AG6_performance_qualified=False)
    except BaseException as error:
        report.update(status="STOP_AG6_CPU_ADAPTER_QUALIFICATION", error=repr(error))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, prior_handler)
        if created:
            report.update(wall_seconds_nonperformance=time.monotonic() - began)
            write("ENTRY_TERMINAL.json", report)
    print(json.dumps(dict(status=report["status"], output=str(OUTPUT),
                         parser_cases_executed=report["parser_cases_executed"],
                         actual_identity_calls=report["actual_identity_calls"],
                         existing_CPU_mapping_calls=report["existing_CPU_mapping_calls"], simulation_starts=0)), flush=True)
    return 0 if report["status"] == "PASS_AG6_CPU_ADAPTER_INTERFACES_ONLY" else 3


if __name__ == "__main__":
    sys.exit(main())
