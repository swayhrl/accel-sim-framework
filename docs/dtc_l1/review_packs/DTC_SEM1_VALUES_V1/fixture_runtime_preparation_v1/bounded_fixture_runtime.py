"""PREPARED_NOT_TESTED. Parent-only finite CPU fixture cohort; no CLI.

No import-time files, resources, launches or registration. Parent must publish
this copied source, exact self/new-fixture roles and matching-ABI freeze first.
This never reuses a build role, runs a simulator CLI, adopts a discovered PID,
or signals a number. The only launch is the fixed diagnostic ELF below.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import types

CORE = "1fcf5113c08a27b64ccca872c4a8fba4c12c1ece"
BUILD = Path("/workspace/dtc-evidence-closure-20261019-v1/sem1/implementation-r1/build")
ELF = str(BUILD / "dtc_l1_sem1_values_ldst")
LIB = str(BUILD / "libcudart.so")
CONFIG = "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
RAW = Path("/workspace/dtc-evidence-closure-20261019-v1/sem1/fixture-runtime-v1")
ROLE = "SEM1_ACTUAL_OBJECT_FIXTURE_RUNTIME_V1"
CLASSIFIER_SHA = "e58caa464124703d65e8d2bd88c6108a2376ef8a01c48b6db8e49273be5a0b61"
PINNED_CORE_SOURCE = {
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/CMakeLists.txt": "a8cd6242380f832f7546a5aadbf5871989260383c9133e1c492fc5b6c3f08ac4",
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/src/gpgpu-sim/dtc-l1-common.h": "d62fee163599ca283aa04f93af9b5cd4b9ff4a97dd15f11547225a3aaaeca334",
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/src/gpgpu-sim/dtc-sem1-values.h": "dd542b4416bd097ca38df0f713359bd35d84b0c49f831239c12d8458530fb841",
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/src/gpgpu-sim/shader.cc": "08c82a639ec6ff441b3d5353cce716fb42ec6e58d93aa9d631f22431959c473c",
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/src/gpgpu-sim/shader.h": "a1ef9529c7e389e77df98337e8b1532e92262166b097f9d9e6d7ceda6a05913b",
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/tests/dtc_l1_sem1_values_ldst.cc": "6904aa940ff16f0e89900ec208fa1f7bef0cf220e6070c2d82486a3a93b2e087",
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/src/gpgpu-sim/gpu-sim.cc": "aeccfeff3c80bd414b0f6dcd53a00e6dd13d426578a9e41d108e45f7b03ce75f",
    "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-sem1-core-174-v1/configs/tested-cfgs/SM7_QV100/gpgpusim.config": "8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3"
}
MODES = ("shared", "masked", "with-e", "ae", "ad", "no-e",
         "wrong-byte", "missing-sector", "wrong-generation", "early-release")
BASE_ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
FLOOR = 5 * 1024**3
OUTPUT_MAX = 32 * 1024**2
START_FREE = FLOOR + OUTPUT_MAX + 128 * 1024**2
LOG_MAX = 512 * 1024
RSS_MAX = 1024**3
TOTAL = 900
WORK = 895
CASE = 60
CLEANUP = 5
INSTANCE = ("boot_id", "pid", "start_ticks", "tgid")
SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGALRM)


class RuntimeStop(RuntimeError):
    pass


def require(value, reason):
    if not value:
        raise RuntimeStop(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest()


def digest(value):
    return (isinstance(value, str) and len(value) == 64 and
            all(x in "0123456789abcdef" for x in value))


def write_new(path, value):
    data = (json.dumps(value, indent=2) + "\n").encode()
    require(len(data) <= 1024**2, "RECEIPT_ONE_MiB_BOUND")
    with Path(path).open("xb") as stream:
        stream.write(data)


def check_files(mapping):
    require(isinstance(mapping, dict) and mapping, "EMPTY_SOURCE_OR_ARTIFACT_CLOSURE")
    for path, expected in mapping.items():
        require(Path(path).is_absolute() and digest(expected) and sha(path) == expected,
                "FROZEN_FILE_CHANGED:" + path)


def disk(path):
    info = os.statvfs(path)
    return info.f_bavail * info.f_frsize


def output_size(root):
    total = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        require(not any((Path(base) / name).is_symlink() for name in dirs),
                "OUTPUT_DIRECTORY_SYMLINK")
        for name in files:
            path = Path(base) / name
            require(not path.is_symlink(), "OUTPUT_FILE_SYMLINK")
            total += path.stat().st_size
    return total


def child_limits():
    signal.pthread_sigmask(signal.SIG_UNBLOCK, SIGNALS)
    resource.setrlimit(resource.RLIMIT_CPU, (30, 31))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (LOG_MAX, LOG_MAX))


def run_exact_fixture_cohort(registration_path, expected_registration_sha256, *,
                             trusted_hashes, manager_role):
    """One standalone parent-published invocation; no retry or arbitrary argv.

    Trusted hash arguments come from the parent's immutable release, separately
    from the registration. Parent must bind CPUAdmission/ownership/shared code
    and all import dependencies from its copied, published closure before call.
    No source in an active build bundle is modified or monkeypatched.
    """
    require(signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL,
            "SOLE_DIRECT_CHILD_WAITER_REQUIRED")
    require(signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0),
            "DO_NOT_REPLACE_EXISTING_PARENT_TIMER")
    require(sys.flags.isolated and sys.dont_write_bytecode and
            dict(os.environ) == BASE_ENV, "ISOLATED_CLEAN_PARENT_ENTRY_REQUIRED")
    began = time.monotonic()
    work_deadline = began + WORK
    interrupted = []
    critical = {"value": False}
    def stop(number, frame):
        interrupted.append(number)
        if critical["value"]:
            return
        raise RuntimeStop("PARENT_SIGNAL_OR_TOTAL_BOUND:" + str(number))
    previous = {number: signal.signal(number, stop) for number in SIGNALS}
    signal.setitimer(signal.ITIMER_REAL, WORK)
    try:
        return _run(registration_path, expected_registration_sha256,
                    deepcopy(trusted_hashes), deepcopy(manager_role),
                    work_deadline, began, interrupted, critical)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        for number, handler in previous.items():
            signal.signal(number, handler)


def _run(registration_path, expected_registration_sha256, trusted, manager_role,
         work_deadline, began, interrupted, critical):
    require(digest(expected_registration_sha256) and
            sha(registration_path) == expected_registration_sha256, "REGISTRATION_CHANGED")
    reg = json.loads(Path(registration_path).read_text())
    require(reg["status"] == "RELEASED_EXACT_SEM1_FIXTURE_RUNTIME_ONLY" and
            reg["total_seconds"] == TOTAL and reg["concurrency"] == 1 and
            reg["modes"] == list(MODES), "FIXED_FINITE_RUNTIME_REGISTRATION_REQUIRED")
    require(reg["admission"]["disk_floor_exclusive_bytes"] == FLOOR,
            "UNCHANGED_STRICT_5GiB_HARD_FLOOR_REQUIRED")
    for field in ("release_sha256", "policy_sha256", "roles_sha256",
                  "manager_role_sha256"):
        require(digest(trusted[field]), "INDEPENDENT_PARENT_TRUST_REQUIRED:" + field)
    require(canonical(manager_role) == trusted["manager_role_sha256"],
            "MANAGER_ROLE_CHANGED")
    for field in ("release", "policy", "roles"):
        require(sha(reg[field + "_path"]) == trusted[field + "_sha256"],
                "PARENT_FROZEN_ARTIFACT_CHANGED:" + field)
    release = json.loads(Path(reg["release_path"]).read_text())
    require(release["status"] == "RELEASED_EXACT_SEM1_FIXTURE_RUNTIME_ONLY" and
            all(release[key] == trusted[key] for key in
                ("policy_sha256", "roles_sha256", "manager_role_sha256")),
            "NOT_THIS_PARENT_RUNTIME_RELEASE")
    policy = json.loads(Path(reg["policy_path"]).read_text())
    require(policy["admission"] == reg["admission"], "ADMISSION_POLICY_CHANGED")
    check_files(reg["source_sha256"])
    check_files(manager_role["source_sha256"])
    require(str(Path(__file__).resolve()) in reg["source_sha256"],
            "RUNTIME_SOURCE_NOT_FROZEN")
    # No module import until the copied closure is fully hash-bound.
    from cpu_admission_v2 import CPUAdmission
    from ownership import identity
    from shared_authority import fresh_process
    from external_cpu_launch_view import ROLE_NAMES
    for name in ("cpu_admission_v2", "ownership", "shared_authority",
                 "external_cpu_launch_view"):
        path = str(Path(sys.modules[name].__file__).resolve())
        require(path in reg["source_sha256"] and
                sha(path) == reg["source_sha256"][path],
                "ADMISSION_MODULE_NOT_IN_FROZEN_CLOSURE:" + name)
    require(ROLE not in ROLE_NAMES and
            manager_role["name"] == "SEM1_ACTUAL_OBJECT_FIXTURE_MANAGER_V1" and
            manager_role["name"] not in ROLE_NAMES,
            "INDEPENDENT_NEW_MANAGER_AND_FIXTURE_ROLES_REQUIRED")
    require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"),
            "RETAINED_PIDFD_REQUIRED")
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    def ident(pid):
        before = identity(pid)
        text = (Path("/proc") / str(pid) / "stat").read_text()
        fields = text[text.rfind(")") + 2:].split()
        after = identity(pid)
        require(all(before[key] == after[key] for key in ("pid", "start_ticks", "tgid")),
                "IDENTITY_CHANGED_DURING_GROUP_READ")
        return dict(after, boot_id=boot, pgrp=int(fields[2]), session=int(fields[3]))
    def image(pid):
        return fresh_process(pid, ident)
    own = ident(os.getpid())
    current = image(own["pid"])
    require(current["argv"] in manager_role["argvs"] and
            current["cwd"] == manager_role["cwd"] and
            current["exe"] == manager_role["executable"] and
            sha(current["exe"]) == manager_role["executable_sha256"] and
            os.path.realpath(sys.executable) == os.path.realpath(current["exe"]),
            "CURRENT_MANAGER_NOT_EXACT_SELFROLE")
    check_files(reg["artifact_sha256"])
    require(all(reg["source_sha256"].get(path) == value for path, value in PINNED_CORE_SOURCE.items()),
            "CRITICAL_PINNED_CORE_SOURCE_CLOSURE_REQUIRED")
    require(reg["artifact_sha256"].get(CONFIG) == PINNED_CORE_SOURCE[CONFIG],
            "PINNED_CONFIG_REQUIRED")
    receipt_path = reg["build_receipt_path"]
    require(receipt_path in reg["artifact_sha256"], "ACTUAL_BUILD_RECEIPT_NOT_FROZEN")
    built = json.loads(Path(receipt_path).read_text())
    require(built["phase"] == "build" and built["core"] == CORE and
            built["exit"] == 0 and built["reason"] is None and
            built["root_terminal"]["reaped"] is True and
            not built["current_group_instances_after_reap"],
            "ACTUAL_MATCHING_ABI_BUILD_NOT_COMPLETE")
    require(all(path in reg["artifact_sha256"] for path in (ELF, LIB, CONFIG)),
            "ELF_LIBRARY_CONFIG_NOT_FROZEN")
    require(sha(reg["abi_freeze_path"]) == reg["abi_freeze_sha256"],
            "ABI_FREEZE_CHANGED")
    abi = json.loads(Path(reg["abi_freeze_path"]).read_text())
    require(abi["core_commit"] == CORE and abi["build_exit"] == 0 and
            abi["matching_fresh_ABI"] is True and abi["assertions_enabled"] is True and
            abi["diagnostic_macro"] == "DTC_SEM1_CONDITIONAL_VALUES=1" and
            abi["elf"] == ELF and abi["library"] == LIB and
            abi["elf_sha256"] == reg["artifact_sha256"][ELF] and
            abi["library_sha256"] == reg["artifact_sha256"][LIB] and
            abi["artifact_sha256"] == reg["artifact_sha256"] and
            abi["loader_and_DT_NEEDED_closure_complete"] is True and
            abi["static_ELF_only_no_ldd"] is True, "MATCHING_ABI_STATIC_FREEZE_REQUIRED")
    require("-O1" in abi["compiler_flags"] and "-g0" in abi["compiler_flags"] and
            not any(x.startswith("-DNDEBUG") for x in abi["compiler_flags"]),
            "MATCHING_ASSERTION_ENABLED_FLAGS_REQUIRED")
    # Import the exact bytes just verified, not a cached same-name module.
    classifier_path = reg["classifier_path"]
    require(reg["source_sha256"].get(classifier_path) == CLASSIFIER_SHA and
            Path(classifier_path).name == "evaluate_fixture_output.py",
            "CLASSIFIER_SOURCE_NOT_FROZEN")
    source = Path(classifier_path).read_bytes()
    require(hashlib.sha256(source).hexdigest() == reg["source_sha256"][classifier_path],
            "CLASSIFIER_CHANGED_BEFORE_IMPORT")
    classifier = types.ModuleType("_parent_frozen_sem1_fixture_classifier")
    exec(compile(source, classifier_path, "exec"), classifier.__dict__)
    require(tuple(classifier.ORDER) == MODES, "CLASSIFIER_MODE_SET_CHANGED")
    roles = json.loads(Path(reg["roles_path"]).read_text())["roles"]
    output = Path(reg["output"])
    require(output.is_absolute() and output.parent == RAW and
            not output.is_symlink(), "NEW_EXACT_OUTPUT_ATTEMPT_REQUIRED")
    rows = [row for row in roles if row["name"] == ROLE]
    fixture_roles = {row["mode"]: row for row in rows}
    require(len(rows) == 10 and set(fixture_roles) == set(MODES),
            "EXACT_TEN_CASE_ROLE_ROWS_REQUIRED")
    for mode, row in fixture_roles.items():
        require(row["executable"] == ELF and
                row["executable_sha256"] == reg["artifact_sha256"][ELF] and
                row["argvs"] == [[ELF, CONFIG, mode]] and
                row["cwd"] == str(output / "cases" / mode) and
                row["source_sha256"] == reg["source_sha256"],
                "EXACT_NEW_FIXTURE_CASE_ROLE_REQUIRED:" + mode)
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases").mkdir()
    active = {"launch": None}
    baseline = {"sample": None}
    results = []

    def validate_self():
        now = image(own["pid"])
        require(all(now[key] == own[key] for key in INSTANCE) and
                now["argv"] in manager_role["argvs"] and
                now["cwd"] == manager_role["cwd"] and
                now["exe"] == manager_role["executable"] and
                sha(now["exe"]) == manager_role["executable_sha256"],
                "CURRENT_EXACT_SELFROLE_CHANGED")
        check_files(manager_role["source_sha256"])

    def exact_live(launch, verify_source=True):
        require(launch is not None and launch["proc"].returncode is None,
                "NO_UNREAPED_DIRECT_POPEN")
        now = ident(launch["proc"].pid)
        require(all(now[key] == launch["instance"][key] for key in INSTANCE),
                "OWN_INSTANCE_CHANGED")
        if now["state"] == "Z":
            return None
        try:
            fresh = image(now["pid"])
        except Exception as error:
            if isinstance(error, RuntimeStop):
                raise
            after = ident(now["pid"])
            if (all(after[key] == launch["instance"][key] for key in INSTANCE)
                    and after["state"] == "Z"):
                return None
            raise
        if verify_source:
            check_files(reg["source_sha256"])
        require(all(fresh[key] == launch["instance"][key] for key in INSTANCE) and
                fresh["argv"] == launch["argv"] and fresh["cwd"] == launch["role"]["cwd"] and
                fresh["exe"] == ELF and fresh["ppid"] == own["pid"] and
                (not verify_source or sha(ELF) == launch["role"]["executable_sha256"]),
                "OWN_CURRENT_IMAGE_CHANGED")
        after = ident(now["pid"])
        require(all(after[key] == launch["instance"][key] for key in INSTANCE),
                "OWN_INSTANCE_CHANGED_AFTER_IMAGE_READ")
        return fresh if after["state"] != "Z" else None

    def join_authority(sample):
        # Frozen review uses 'role' for new ordinary exact roles, not role_name.
        for row in sample["authority"].get("exact_external_CPU_controls", []):
            if row.get("role") != ROLE:
                continue
            launch = active["launch"]
            require(launch is not None and launch["proc"].returncode is None,
                    "FIXTURE_ROLE_WITHOUT_THIS_UNREAPED_DIRECT_POPEN")
            require(row["pid"] == launch["instance"]["pid"] and
                    row["start_ticks"] == launch["instance"]["start_ticks"],
                    "FOREIGN_MATCHING_FIXTURE_ROLE_NO_ADOPTION")
            # A saved accepted row is not a current image. Re-read both sides.
            fresh = exact_live(launch)
            if fresh is not None:
                launch["live_observed"] = True
                launch["last_actual_live_image"] = fresh

    class FixtureCPUAdmission(CPUAdmission):
        def sample(self):
            value = super().sample()
            value["coordinator_mount_disk_free"] = value["disk_free"]
            value["coordinator_mount_device"] = value["output_filesystem_device"]
            value["disk_free"] = disk(output)
            value["output_filesystem_device"] = output.stat().st_dev
            join_authority(value)
            if baseline["sample"] is None:
                baseline["sample"] = deepcopy(value)
            return value
        def checks(self, sample):
            values = super().checks(sample)
            old = baseline["sample"]
            values["actual_output_mount_strictly_gt5GiB"] = sample["disk_free"] > FLOOR
            values["no_new_cohort_host_oom"] = sample["host_oom_kill"] == old["host_oom_kill"]
            values["no_new_cohort_cgroup_oom"] = all(
                sample["cgroup_events"][key] == old["cgroup_events"][key]
                for key in ("oom", "oom_kill"))
            return values

    def session_instances(root):
        # Read-only inspection, never ownership adoption or signal targets.
        found = []
        for path in Path("/proc").iterdir():
            if not path.name.isdigit():
                continue
            try:
                text = (path / "stat").read_text()
                fields = text[text.rfind(")") + 2:].split()
                if int(fields[2]) == root["pid"] or int(fields[3]) == root["pid"]:
                    found.append({"pid": int(path.name), "pgrp": int(fields[2]),
                        "session": int(fields[3]), "start_ticks": int(fields[19])})
            except (FileNotFoundError, ProcessLookupError):
                continue
        return found

    def cleanup(launch):
        proc, fd = launch["proc"], launch["pidfd"]
        stopped = {"signals": [], "reaped": proc.returncode is not None}
        if proc.returncode is not None:
            return stopped
        deadline = launch.setdefault("cleanup_deadline",
                    min(time.monotonic() + CLEANUP, began + TOTAL))
        launch["cleanup_attempted"] = True
        # Repeated TERM/ALRM must not interrupt the finite own-finally cleanup.
        saved = {number: signal.signal(number,
                 lambda number, frame: interrupted.append(number)) for number in SIGNALS}
        try:
            try:
                fresh = exact_live(launch, verify_source=False)
                require(time.monotonic() < deadline, "CLEANUP_DEADLINE")
                if fresh is not None:
                    signal.pidfd_send_signal(fd, signal.SIGTERM)
                    stopped["signals"].append("SIGTERM_PIDFD")
                proc.wait(timeout=max(.001, min(2, deadline - time.monotonic())))
            except subprocess.TimeoutExpired:
                fresh = exact_live(launch, verify_source=False)
                require(time.monotonic() < deadline, "CLEANUP_DEADLINE")
                if fresh is not None:
                    signal.pidfd_send_signal(fd, signal.SIGKILL)
                    stopped["signals"].append("SIGKILL_PIDFD")
                proc.wait(timeout=max(.001, deadline - time.monotonic()))
            except (FileNotFoundError, ProcessLookupError):
                # Natural exit race: direct wait only; no numeric fallback.
                proc.wait(timeout=max(.001, deadline - time.monotonic()))
            stopped["reaped"] = proc.returncode is not None
        except BaseException as error:
            stopped.update(status="CLEANUP_UNRESOLVED", error=repr(error),
                           reaped=proc.returncode is not None)
        finally:
            for number, handler in saved.items():
                signal.signal(number, handler)
        return stopped

    def resources(gate, dest, name):
        validate_self()
        sample = gate.sample()
        checks = gate.checks(sample)
        write_new(dest / name, {"sample": sample, "checks": checks})
        require(all(checks.values()), "RESOURCE_OR_AUTHORITY_CHANGED")
        require(disk(output) > FLOOR and output_size(output) <= OUTPUT_MAX,
                "ACTUAL_OUTPUT_DISK_OR_32MiB_BOUND")
        return sample

    def execute(mode):
        require(active["launch"] is None and not interrupted, "NO_PARALLEL_OR_INTERRUPTED_CASE")
        dest = output / "cases" / mode
        dest.mkdir()
        # New complete CPUAdmission object and >=10s pair for every single case.
        fixture = fixture_roles[mode]
        gate = FixtureCPUAdmission(reg, [manager_role, fixture])
        launch, reason, stopped = None, None, None
        logs = (dest / "stdout.log", dest / "stderr.log")
        try:
            require(disk(output) >= START_FREE and output_size(output) <= OUTPUT_MAX,
                    "START_OUTPUT_WRITING_RESERVE")
            check_files(reg["source_sha256"])
            check_files(reg["artifact_sha256"])
            validate_self()
            require(gate.admit(dest / "admission"), "WAIT_ADMISSION_NO_CHILD_NO_RETRY")
            second = json.loads((dest / "admission" / "SECOND.json").read_text())
            require(time.monotonic() < work_deadline, "TOTAL_WORK_BOUND_NO_START")
            check_files(reg["source_sha256"])
            check_files(reg["artifact_sha256"])
            validate_self()
            require(0 <= time.monotonic_ns() - second["monotonic_ns"] <= 5 * 10**9 and
                    disk(output) >= START_FREE, "ADMISSION_STALE_OR_DISK_CHANGED")
            tmp = dest / "tmp"
            tmp.mkdir()
            env = dict(BASE_ENV, CUDA_VISIBLE_DEVICES="", LD_LIBRARY_PATH=str(BUILD),
                       TMPDIR=str(tmp))
            argv = [ELF, CONFIG, mode]
            case_deadline = min(time.monotonic() + CASE, work_deadline)
            signal.setitimer(signal.ITIMER_REAL,
                             max(.001, case_deadline - time.monotonic()))
            with logs[0].open("xb") as stdout, logs[1].open("xb") as stderr:
                require(len(list((Path("/proc") / str(own["pid"]) / "task").iterdir())) == 1,
                        "SINGLE_THREADED_PREEXEC_PARENT_REQUIRED")
                critical["value"] = True  # retain handle before signal can raise
                proc = subprocess.Popen(argv, cwd=fixture["cwd"], env=env,
                    stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                    close_fds=True, start_new_session=True, preexec_fn=child_limits)
                # Retain Popen immediately, even if identity/pidfd acquisition fails.
                launch = {"proc": proc, "pidfd": None, "instance": None, "argv": argv,
                          "live_observed": False, "last_actual_live_image": None, "role": fixture}
                active["launch"] = launch
                try:
                    critical["value"] = False
                    require(not interrupted, "SIGNAL_AT_POPEN_BOUNDARY")
                    launch["instance"] = ident(proc.pid)  # before poll/wait/reap
                    launch["pidfd"] = os.pidfd_open(proc.pid)
                    require(launch["instance"]["ppid"] == own["pid"] and
                            launch["instance"]["pgrp"] == proc.pid and
                            launch["instance"]["session"] == proc.pid,
                            "DIRECT_CHILD_PARENT_OR_SESSION_CHANGED")
                    write_new(dest / "START.json", {
                        "actual_Popen": True, "instance": launch["instance"],
                        "argv": argv, "cwd": fixture["cwd"], "env": env,
                        "manager_instance": own, "launched_monotonic_ns": time.monotonic_ns(),
                        "deadline_monotonic": case_deadline, "trusted": trusted})
                    sample_number = 0
                    while True:
                        resources(gate, dest, "RESOURCE_%04d.json" % sample_number)
                        sample_number += 1
                        require(not interrupted, "INTERRUPTED")
                        require(all(path.stat().st_size <= LOG_MAX for path in logs),
                                "512KiB_PER_STREAM_LOG_BOUND")
                        # Current task metadata only, never adoption or signalling.
                        task_paths = list((Path("/proc") / str(proc.pid) / "task").glob("*"))
                        require(len(task_paths) <= 4, "UNEXPECTED_TASK_COUNT")
                        for task in task_paths:
                            try:
                                children = (task / "children").read_text().strip()
                                require(not children, "UNEXPECTED_DESCENDANTS_CLEANUP_UNRESOLVED")
                            except (FileNotFoundError, ProcessLookupError):
                                pass
                        try:
                            text = (Path("/proc") / str(proc.pid) / "status").read_text()
                            rss = next((int(line.split()[1]) * 1024 for line in text.splitlines()
                                        if line.startswith("VmRSS:")), 0)
                            require(rss <= RSS_MAX, "ROOT_RSS_ONE_GiB_BOUND")
                        except (FileNotFoundError, ProcessLookupError):
                            pass
                        if proc.poll() is not None:  # after this, never signal
                            break
                        require(time.monotonic() < case_deadline, "CASE_TIMEOUT")
                        time.sleep(.2)
                except BaseException as error:
                    reason = repr(error)
                finally:
                    critical["value"] = True
                    if proc.returncode is None:
                        if launch["instance"] is not None and launch["pidfd"] is not None:
                            stopped = cleanup(launch)
                        else:
                            # No identity/pidfd -> wait own handle only; no fallback signal.
                            try:
                                proc.wait(timeout=min(CLEANUP, max(.001, began + TOTAL - time.monotonic())))
                                stopped = {"reaped": True, "signals": [],
                                           "identity": "UNAVAILABLE_NO_SIGNAL"}
                            except BaseException as error:
                                stopped = {"reaped": False, "signals": [],
                                           "status": "CLEANUP_UNRESOLVED", "error": repr(error)}
                    else:
                        stopped = {"reaped": True, "signals": []}
                    if launch["pidfd"] is not None and stopped.get("reaped"):
                        os.close(launch["pidfd"])
                        launch["pidfd"] = None
                    if stopped.get("reaped"):
                        active["launch"] = None
                    else:
                        reason = reason or "CLEANUP_UNRESOLVED"
                    if launch["instance"] is not None:
                        leftovers = session_instances(launch["instance"])
                        if leftovers:
                            reason = reason or "CLEANUP_UNRESOLVED_SESSION_OR_GROUP"
                    else:
                        leftovers = "UNAVAILABLE_START_IDENTITY"
                        reason = reason or "START_IDENTITY_UNAVAILABLE"
                    launch["leftovers_after_reap_readonly"] = leftovers
                    critical["value"] = False
            require(not interrupted, "SIGNAL_DURING_OWN_FINALLY_CLEANUP")
            require(reason is None, reason or "CASE_FAILURE")
            resources(gate, dest, "FINAL_RESOURCE.json")
            require(all(path.stat().st_size <= LOG_MAX for path in logs),
                    "FINAL_LOG_BOUND")
            verdict = classifier.classify(mode, proc.returncode,
                logs[0].read_bytes(), logs[1].read_bytes(), expected_library_path=LIB,
                execution_failure_reason=None)
            require(verdict["status"] in ("CONDITIONAL_SECTOR_VALUES",
                    "CONDITIONAL_COUNTERMODEL", "EXPECTED_TARGETED_REJECTION"),
                    "OUTPUT_PROTOCOL_REJECT:" + repr(verdict))
        except BaseException as error:
            reason = reason or repr(error)
            verdict = {"status": "STOP_CASE", "reason": reason}
        finally:
            critical["value"] = False
            signal.setitimer(signal.ITIMER_REAL,
                             max(.001, work_deadline - time.monotonic()))
        result = {"mode": mode, "status": verdict["status"], "reason": reason,
            "popen_returned": launch is not None, "actual_instance": launch["instance"] if launch else None,
            "returncode": launch["proc"].returncode if launch else None,
            "cleanup": stopped, "leftovers": launch.get("leftovers_after_reap_readonly") if launch else None,
            "live_observation": "OBSERVED_CURRENT_DIRECT_CHILD" if launch and launch["live_observed"]
                                else "UNAVAILABLE_NO_RETRY",
            "last_actual_live_image": launch["last_actual_live_image"] if launch else None,
            "classification": verdict, "simulation_starts": 0, "native": "UNPROVEN"}
        write_new(dest / "TERMINAL.json", result)
        return result

    failure = None
    try:
        write_new(output / "MANAGER_START.json", {"manager": own,
            "registration_sha256": expected_registration_sha256, "trusted": trusted,
            "total_seconds": TOTAL, "concurrency": 1, "role": ROLE})
        for mode in MODES:
            result = execute(mode)
            results.append(result)
            if result["reason"] is not None:
                break
    except BaseException as error:
        failure = repr(error)
    finally:
        critical["value"] = True
        remaining = active["launch"]
        if remaining is not None:
            if remaining.get("cleanup_attempted"):
                emergency = {"status": "CLEANUP_UNRESOLVED_NO_SECOND_SIGNAL_ATTEMPT",
                             "reaped": remaining["proc"].returncode is not None}
            elif remaining["instance"] is not None and remaining["pidfd"] is not None:
                emergency = cleanup(remaining)
            else:
                try:
                    remaining["proc"].wait(timeout=min(CLEANUP,
                        max(.001, began + TOTAL - time.monotonic())))
                    emergency = {"reaped": True, "signals": [], "identity": "UNAVAILABLE"}
                except BaseException as error:
                    emergency = {"reaped": False, "signals": [],
                                 "status": "CLEANUP_UNRESOLVED", "error": repr(error)}
            if remaining["pidfd"] is not None:
                os.close(remaining["pidfd"])
                remaining["pidfd"] = None
            if remaining["instance"] is not None:
                emergency["postreap_readonly_session_instances"] = session_instances(remaining["instance"])
            failure = failure or "EMERGENCY_OWN_CLEANUP_REQUIRED"
            write_new(output / "EMERGENCY_CLEANUP.json", emergency)
        critical["value"] = False
    report = {"status": "COMPLETE_CONDITIONAL_FIXTURE_COHORT_ONLY" if
              failure is None and not interrupted and len(results) == 10 and all(r["reason"] is None for r in results)
              else "STOP_FINITE_FIXTURE_COHORT",
              "failure": failure, "cases": results, "actual_Popen_count": sum(r["popen_returned"] for r in results),
              "simulation_starts": 0, "native": "UNPROVEN", "architectural_values": "UNPROVEN",
              "elapsed_seconds": time.monotonic() - began,
              "short_process_live_observation_misses_are_not_retried": True}
    write_new(output / "MANAGER_RESULT.json", report)
    return report
