"""SOURCE_PREPARED_NOT_EXECUTED: fixed sequential real CPU work, never a sim CLI.

The parent's source-bound entry calls run_exact_cpu_roles with independently
pinned registration/release/role/policy/manager-role digests. No CLI, discovery,
retry, background worker, new test suite or import-time action is provided.
Only local direct-Popen handles/pidfds can perform cleanup; provider exports
data copies only. CPUAdmission must have the parent's external-view parameter.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


PYTHON = "/usr/bin/python3.10"
RAW = Path("/workspace/dtc-evidence-closure-20261019-v1")
TOTAL_SECONDS = 2800
CLEANUP_SECONDS = 30
WORK_SECONDS = TOTAL_SECONDS - CLEANUP_SECONDS
MAX_LOG_BYTES = 16 * 1024**2
BASE_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
COV_ROLE = "COV1_TINY_MATH_REFERENCE_FOUR_TESTS"
SEM_ROLE = "SEM1_BOUNDED_DIAGNOSTIC_BUILD_CONTROL"
ROB_ROLE = "ROB1_BOUNDED_DIAGNOSTIC_BUILD_CONTROL"
_SEM = "/workspace/worktrees/accel-sim-iscas2027-dtc-sem1-values-174-v1"
_ROB = "/workspace/worktrees/accel-sim-iscas2027-dtc-rob1-controls-174-v1"
_COV = "/workspace/worktrees/accel-sim-iscas2027-dtc-cov1-inputs-174-v1"
# key, role, phase, cwd, script, wall budget. No SEM configure entry exists.
PHASES = (
    ("sem_build", SEM_ROLE, "build", _SEM,
     _SEM + "/docs/dtc_l1/review_packs/DTC_SEM1_VALUES_V1/implementation_r1/bounded_cpu_build.py", 1230),
    ("rob_configure", ROB_ROLE, "configure", _ROB,
     _ROB + "/docs/dtc_l1/review_packs/DTC_ROB1_CONTROLS_V1/implementation_r1/bounded_cpu_build.py", 90),
    ("rob_build", ROB_ROLE, "build", _ROB,
     _ROB + "/docs/dtc_l1/review_packs/DTC_ROB1_CONTROLS_V1/implementation_r1/bounded_cpu_build.py", 1230),
    ("cov_observe_once", COV_ROLE, "test", _COV,
     _COV + "/docs/dtc_l1/review_packs/DTC_COV1_INPUTS_V1/reference/test_reference_algorithms.py", 60),
)
RECEIPTS = {
    "sem_configure": RAW / "sem1/implementation-r1/configure.receipt.json",
    "sem_build": RAW / "sem1/implementation-r1/build.receipt.json",
    "rob_configure": RAW / "rob1/ldst-qualification-r1/configure.receipt.json",
    "rob_build": RAW / "rob1/ldst-qualification-r1/build.receipt.json",
}


class ManagerStop(RuntimeError):
    pass


def require(value, reason):
    if not value:
        raise ManagerStop(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest()


def write_new(path, value):
    with Path(path).open("x") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def _controller_receipt(key, expected_sha=None):
    path = RECEIPTS[key]
    if expected_sha is not None:
        require(sha(path) == expected_sha, "COMPLETED_PHASE_RECEIPT_CHANGED:" + key)
    value = json.loads(path.read_text())
    phase = "configure" if key.endswith("configure") else "build"
    require(value["phase"] == phase and value["exit"] == 0 and
            value["reason"] is None and value["root_terminal"]["reaped"] is True and
            not value["current_group_instances_after_reap"],
            "CONTROLLER_PHASE_NOT_COMPLETE:" + key)
    return {"path": str(path), "sha256": sha(path), "controller_exit": 0}


def _run_exact_cpu_roles(registration_path, expected_registration_sha256, *,
                         trusted_hashes, manager_role, work_deadline):
    """Parent-only entry; all expected hashes come from its pinned release.

    Parent imports/binds its current cpu_admission_v2, shared_authority,
    ownership and external_cpu_launch_view sources before this call. No
    arbitrary argv/environment/job list is accepted from registration.
    """
    trusted_hashes = deepcopy(trusted_hashes)
    manager_role = deepcopy(manager_role)
    require(sha(registration_path) == expected_registration_sha256,
            "MANAGER_REGISTRATION_CHANGED")
    registration = json.loads(Path(registration_path).read_text())
    require(registration["status"] == "REGISTERED_FOR_EXACT_CPU_ROLE_MANAGER_ONLY",
            "MANAGER_NOT_RELEASED")
    require(registration["total_timeout_seconds"] == TOTAL_SECONDS and
            registration["concurrency"] == 1, "FIXED_SEQUENTIAL_MANAGER_BOUND_REQUIRED")
    require(type(registration["include_cov"]) is bool, "FIXED_COV_OBSERVATION_FLAG_REQUIRED")
    for name in ("release_sha256", "role_contract_sha256", "admission_policy_sha256",
                 "manager_role_sha256"):
        value = trusted_hashes[name]
        require(isinstance(value, str) and len(value) == 64 and
                all(c in "0123456789abcdef" for c in value), "FIXED_TRUST_HASH_REQUIRED:" + name)
    require(canonical_sha(manager_role) == trusted_hashes["manager_role_sha256"],
            "INDEPENDENT_MANAGER_ROLE_CHANGED")
    for path, digest in registration["source_sha256"].items():
        require(sha(path) == digest, "REGISTERED_SOURCE_CHANGED:" + path)
    for field, digest_name in (("release_path", "release_sha256"),
                               ("role_contract_path", "role_contract_sha256"),
                               ("admission_policy_path", "admission_policy_sha256")):
        require(sha(registration[field]) == trusted_hashes[digest_name],
                "FIXED_PARENT_ARTIFACT_CHANGED:" + field)
    release = json.loads(Path(registration["release_path"]).read_text())
    require(release["status"] == "RELEASED_EXACT_CPU_ROLE_MANAGER_ONLY" and
            all(release[k] == trusted_hashes[k] for k in
                ("role_contract_sha256", "admission_policy_sha256", "manager_role_sha256")),
            "PARENT_RELEASE_NOT_THIS_ROLE_COHORT")
    policy = json.loads(Path(registration["admission_policy_path"]).read_text())
    require(policy["admission"] == registration["admission"], "CPU_ADMISSION_POLICY_CHANGED")
    roles = {r["name"]: r for r in json.loads(Path(
        registration["role_contract_path"]).read_text())["roles"]}
    completed = registration["completed_phase_receipts"]
    require("sem_configure" in completed and set(completed) <= set(RECEIPTS),
            "SEM_CONFIGURE_IMPORT_REQUIRED_NO_CONFIGURE_RESTART")
    imports = {key: _controller_receipt(key, digest) for key, digest in completed.items()}
    output = Path(registration["manager_output"]).resolve()
    require(output.is_relative_to(RAW / "coordinator/cpu-qualification"),
            "MANAGER_OUTPUT_NOT_ISOLATED")
    output.mkdir(parents=True, exist_ok=False)

    # These are the parent's frozen implementations, not provider-selected code.
    from cpu_admission_v2 import CPUAdmission
    from shared_authority import fresh_process
    from ownership import identity
    from external_cpu_launch_view import ExternalCPULaunchView

    boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    def current_identity(pid):
        return dict(identity(pid), boot_id=boot_id)
    def current_process(pid):
        return fresh_process(pid, current_identity)
    own = current_identity(os.getpid())
    actual_manager = current_process(own["pid"])
    require(actual_manager["argv"] in manager_role["argvs"] and
            actual_manager["cwd"] == manager_role["cwd"] and
            actual_manager["exe"] == manager_role["executable"] and
            sha(actual_manager["exe"]) == manager_role["executable_sha256"],
            "MANAGER_CURRENT_EXECUTION_NOT_REGISTERED")
    for path, digest in manager_role["source_sha256"].items():
        require(sha(path) == digest, "MANAGER_SOURCE_CHANGED:" + path)
    require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"),
            "PIDFD_ONLY_CLEANUP_REQUIRED")

    phase_roles = {}
    for key, role_name, phase, cwd, script, seconds in PHASES:
        argv = [PYTHON, "-E" if role_name == COV_ROLE else "-I", "-B", script,
                "-v" if role_name == COV_ROLE else phase]
        role = roles[role_name]
        require(argv in role["argvs"] and role["cwd"] == cwd and
                role["executable"] == PYTHON, "EXACT_PHASE_COMMAND_NOT_REGISTERED:" + key)
        spec = phase_roles.setdefault(role_name, dict(role, phases={}))
        spec["phases"][phase] = {"argv": argv, "max_runtime_ns": seconds * 10**9,
            "output_bound_bytes": (1024**2 if role_name == COV_ROLE else
                                   512 * 1024**2 + 2 * MAX_LOG_BYTES)}
    trust = dict(trusted_hashes, manager=dict(manager_role, instance=own,
                 argv=actual_manager["argv"]), roles=phase_roles)
    # Provider state has only data; handles/pidfds are local to execute_phase.
    launches, admissions, results = [], {}, []
    binding_probe = {"passed": False}
    def provider():
        return {"manager_instance": deepcopy(own),
                "manager_role_sha256": trusted_hashes["manager_role_sha256"],
                "launches": deepcopy(launches)}
    def view():
        return ExternalCPULaunchView(trusted=trust, admissions=admissions,
            provider=provider, identity_reader=current_identity,
            process_reader=current_process)
    gate = CPUAdmission(registration, [manager_role], external_launch_view_provider=view)
    total_deadline = work_deadline

    def cleanup(proc, pidfd, instance, argv, cwd):
        """Never poll/reap then signal; never signal a number, group or peer."""
        if proc.returncode is not None:
            return {"signal_sent": False, "reaped": True}
        sent, error = False, None
        cleanup_deadline = time.monotonic() + CLEANUP_SECONDS
        try:
            live = current_identity(proc.pid)
            require(all(live[k] == instance[k] for k in
                        ("boot_id", "pid", "start_ticks", "tgid")),
                    "CLEANUP_INSTANCE_CHANGED_NO_SIGNAL")
            if live["state"] != "Z":
                image = current_process(proc.pid)
                require(pidfd is not None and image["argv"] == argv and
                        image["cwd"] == cwd and image["exe"] == PYTHON and
                        image["ppid"] == own["pid"], "CLEANUP_NOT_EXACT_OWN_PYTHON")
                signal.pidfd_send_signal(pidfd, signal.SIGTERM)
                sent = True
        except (OSError, ValueError, ManagerStop) as failure:
            error = repr(failure)
        # Waiting this still-owned direct handle is allowed even when a fresh
        # identity read lost a natural-exit race. Never retry or replace a signal.
        try:
            proc.wait(timeout=max(.001, cleanup_deadline - time.monotonic()))
            return {"signal_sent": sent, "reaped": True, "identity_or_signal_error": error}
        except (subprocess.TimeoutExpired, ManagerStop) as failure:
            return {"signal_sent": sent, "reaped": False,
                    "status": "UNRESOLVED_OWN_CONTROLLER_NO_FALLBACK_SIGNAL",
                    "error": error or repr(failure)}

    def execute_phase(item):
        key, role_name, phase, cwd, script, seconds = item
        if key in imports:
            return {"phase_key": key, "status": "PRESERVED_COMPLETED_NO_START",
                    "receipt": imports[key], "live_observed": False}
        if key == "cov_observe_once" and not registration["include_cov"]:
            return {"phase_key": key, "status": "COV_NOT_REQUESTED_NO_START", "live_observed": False}
        if key in RECEIPTS:
            receipt = RECEIPTS[key]
            require(not receipt.exists() and not receipt.with_name(phase + ".log").exists(),
                    "PRESERVE_EXISTING_PHASE_ARTIFACT:" + key)
        if key == "rob_build":
            _controller_receipt("rob_configure")
        dest = output / key
        dest.mkdir(exist_ok=False)
        if not gate.admit(dest / "admission"):
            return {"phase_key": key, "status": "WAIT_RESOURCE_OR_AUTHORITY_NO_START", "live_observed": False}
        admitted = json.loads((dest / "admission/ADMISSION.json").read_text())
        require(admitted["status"] == "PASS_CPU_ADMISSION_ONLY", "ACTUAL_PHASE_ADMISSION_REQUIRED")
        last_sample = json.loads((dest / "admission/SECOND.json").read_text())
        began = time.monotonic_ns()
        require(0 <= began - last_sample["monotonic_ns"] <= 5 * 10**9,
                "ADMISSION_STALE_NO_START")
        seconds_left = min(seconds, total_deadline - time.monotonic())
        require(seconds_left > 0, "MANAGER_TOTAL_BOUND_NO_START")
        deadline = began + int(seconds_left * 10**9)
        argv = phase_roles[role_name]["phases"][phase]["argv"]
        env = dict(BASE_ENV)
        if role_name == COV_ROLE:
            env.update(CUDA_VISIBLE_DEVICES="", PYTHONDONTWRITEBYTECODE="1")
        spec = phase_roles[role_name]
        for path, digest in registration["phase_preflight_sha256"][key].items():
            require(sha(path) == digest, "PHASE_CONFIG_TOOL_BINDING_CHANGED_NO_START:" + path)
        for path, digest in spec["source_sha256"].items():
            require(sha(path) == digest, "PHASE_SOURCE_CHANGED_NO_START:" + path)
        require(sha(PYTHON) == spec["executable_sha256"], "PHASE_PYTHON_CHANGED_NO_START")
        admissions.setdefault(role_name, {})[phase] = {
            "receipt_sha256": sha(dest / "admission/ADMISSION.json"),
            "policy_sha256": trusted_hashes["admission_policy_sha256"],
            "status": "PASS", "scope": "CPU_ONLY",
            "valid_from_monotonic_ns": last_sample["monotonic_ns"],
            "valid_until_monotonic_ns": deadline}
        proc = None
        pidfd = None
        instance = None
        row = None
        reason = None
        observed = False
        stopped = {"signal_sent": False, "reaped": False}
        with (dest / "stdout").open("xb") as stdout, (dest / "stderr").open("xb") as stderr:
            try:
                require(0 <= time.monotonic_ns() - last_sample["monotonic_ns"] <= 5 * 10**9,
                        "ADMISSION_STALE_AFTER_HASH_NO_START")
                proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                        stdout=stdout, stderr=stderr, close_fds=True)
                instance = current_identity(proc.pid)  # before any wait/poll can reap
                pidfd = os.pidfd_open(proc.pid)
                row = {"role_name": role_name, "phase": phase, "instance": instance,
                       "manager_instance": own, "actual_launch_id": key + ":" + str(began),
                       "state": "ACTIVE", "argv": argv, "cwd": cwd, "executable": PYTHON,
                       "launched_monotonic_ns": began, "deadline_monotonic_ns": deadline,
                       "output_bound_bytes": spec["phases"][phase]["output_bound_bytes"],
                       "admission_sha256": admissions[role_name][phase]["receipt_sha256"],
                       **{k: trusted_hashes[k] for k in
                          ("release_sha256", "role_contract_sha256", "admission_policy_sha256")}}
                launches.append(row)
                write_new(dest / "START.json", dict(row, environment=env))
                snapshot, verdict = gate.review(own)  # same real callback, once, no saved live row
                accepted = verdict.get("exact_external_CPU_controls", [])
                observed = any(x.get("live_observation") and x.get("role_name") == role_name and
                               x.get("pid") == instance["pid"] and
                               x.get("start_ticks") == instance["start_ticks"] for x in accepted)
                write_new(dest / "OBSERVATION.json", {"authority": verdict,
                    "original_process_count": len(snapshot["processes"]),
                    "original_snapshot_sha256": canonical_sha(snapshot), "live_observed": observed})
                require(verdict["status"] == "PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY",
                        "ACTUAL_CALLBACK_AUTHORITY_NOT_PASS")
                if observed and not binding_probe["passed"]:
                    # One read-only mismatch query against this same actually
                    # live control; no altered process, second child or suite.
                    from external_cpu_launch_view import ExternalCPUReject
                    current = current_identity(proc.pid)
                    require(current["start_ticks"] == instance["start_ticks"] and
                            current["state"] != "Z", "BINDING_PROBE_ROLE_ALREADY_TERMINAL")
                    def bad_provider():
                        data = provider()
                        for launch in data["launches"]:
                            if launch["actual_launch_id"] == row["actual_launch_id"]:
                                launch["release_sha256"] = "0" * 64
                        return data
                    probe = ExternalCPULaunchView(trusted=trust, admissions=admissions,
                        provider=bad_provider, identity_reader=current_identity,
                        process_reader=current_process)
                    try:
                        probe.observe(role_name, dict(current, is_simulator=False),
                                      callback_sample_id=key+":actual-binding-negative")
                    except ExternalCPUReject as failure:
                        require("EXTERNAL_BINDING_CHANGED:release_sha256" in str(failure),
                                "BINDING_PROBE_WRONG_REJECT")
                        binding_probe.update(passed=True, reason=str(failure),
                            actual_instance=current, phase_key=key,
                            source_registration_sha256=expected_registration_sha256)
                        write_new(dest / "ACTUAL_BINDING_REJECTION.json", binding_probe)
                    else:
                        raise ManagerStop("ADMISSION_BINDING_MISMATCH_ACCEPTED")
                proc.wait(timeout=max(.001, (deadline - time.monotonic_ns()) / 10**9))
                stopped = {"signal_sent": False, "reaped": True}
            except BaseException as error:
                reason = repr(error)
            finally:
                if proc is not None and proc.returncode is None:
                    if instance is not None:
                        stopped = cleanup(proc, pidfd, instance, argv, cwd)
                    else:
                        # The returned direct handle remains our child even
                        # when no exact identity was readable. Wait only; no
                        # identity means no signal, discovery or replacement.
                        try:
                            proc.wait(timeout=CLEANUP_SECONDS)
                            stopped = {"signal_sent": False, "reaped": True,
                                       "status": "OWN_HANDLE_REAPED_NO_INSTANCE_NO_SIGNAL"}
                        except (subprocess.TimeoutExpired, ManagerStop) as failure:
                            stopped = {"signal_sent": False, "reaped": False,
                                       "status": "UNRESOLVED_NO_INSTANCE_NO_SIGNAL",
                                       "error": repr(failure)}
                if row is not None and proc.returncode is not None:
                    row["state"] = "TERMINAL_REAPED"
                if pidfd is not None:
                    os.close(pidfd)
        code = proc.returncode if proc else None
        if any((dest / name).stat().st_size > MAX_LOG_BYTES for name in ("stdout", "stderr")):
            reason = reason or "MANAGER_ROLE_LOG_BOUND_EXCEEDED"
        if role_name == COV_ROLE and sum((dest / name).stat().st_size for name in
                                        ("stdout", "stderr")) > 1024**2:
            reason = reason or "COV_ONE_MiB_OUTPUT_BOUND_EXCEEDED"
        receipt = None
        if reason is None and code == 0 and key in RECEIPTS:
            try:
                receipt = _controller_receipt(key)
            except (OSError, KeyError, ValueError, ManagerStop) as error:
                reason = repr(error)
        result = {"phase_key": key, "role_name": role_name, "controller_returncode": code,
                  "popen_returned": proc is not None,
                  "actual_instance": instance, "live_observed": observed, "reason": reason,
                  "cleanup": stopped, "receipt": receipt,
                  "status": "ACTUAL_CONTROLLER_EXIT0" if code == 0 and reason is None else "STOP_PHASE_INCOMPLETE"}
        write_new(dest / "TERMINAL.json", result)
        return result

    failure = None
    try:
        write_new(output / "MANAGER_START.json", {"manager": own,
            "registration_sha256": expected_registration_sha256, "trusted_hashes": trusted_hashes,
            "total_seconds": TOTAL_SECONDS, "concurrency": 1, "completed_imports": imports})
        for item in PHASES:  # fixed four-phase sequence, no retry/dispatch loop
            result = execute_phase(item)
            results.append(result)
            if result["status"].startswith(("WAIT_", "STOP_")):
                break
    except BaseException as error:
        failure = repr(error)
    seen = {r.get("role_name") for r in results if r.get("live_observed")}
    complete = (failure is None and len(results) == len(PHASES) and
                all(not r["status"].startswith(("WAIT_", "STOP_")) for r in results))
    report = {"status": ("PASS_PER_ROLE_CPU_OBSERVATIONS_ONLY" if complete and
              {SEM_ROLE, ROB_ROLE, COV_ROLE} <= seen and binding_probe["passed"] else "CPU_ROLE_MANAGER_INCOMPLETE"),
              "failure": failure, "actual_binding_probe": binding_probe, "phases": results, "observed_roles": sorted(x for x in seen if x),
              "actual_controller_invocations": sum(bool(r.get("popen_returned")) for r in results),
              "joint_three_role_observation": False, "continuous_global_authority": False,
              "simulation_starts": 0, "completed_imports": imports,
              "provider_exports_handles_or_signal_rights": False}
    write_new(output / "MANAGER_RESULT.json", report)
    return report


def run_exact_cpu_roles(registration_path, expected_registration_sha256, *,
                        trusted_hashes, manager_role):
    """Standalone registered parent entry only; finite bootstrap/work/cleanup.

    2770s work alarm includes imports/binding/admissions; reserve at most30s
    for the one local controller's TERM cleanup. No existing timer is extended.
    Parent entry must retain its own outer start/terminal receipt on exception.
    """
    require(signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL,
            "MANAGER_MUST_BE_SOLE_DIRECT_CHILD_WAITER")
    require(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0),
            "STANDALONE_MANAGER_MUST_NOT_REPLACE_PARENT_TIMER")
    def interrupt(number, frame):
        raise ManagerStop("MANAGER_SIGNAL_OR_TOTAL_BOUND:" + str(number))
    previous = {number: signal.signal(number, interrupt) for number in
                (signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGALRM)}
    work_deadline = time.monotonic() + WORK_SECONDS
    signal.setitimer(signal.ITIMER_REAL, WORK_SECONDS)
    try:
        return _run_exact_cpu_roles(registration_path, expected_registration_sha256,
            trusted_hashes=trusted_hashes, manager_role=manager_role,
            work_deadline=work_deadline)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        for number, handler in previous.items():
            signal.signal(number, handler)
