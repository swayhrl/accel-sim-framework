"""SOURCE_PREPARED_NOT_EXECUTED. Parent-published single-call fixture entry.

Copy unchanged to execution/prepared_sem1_fixture_runtime_v1, then parent must
finalize/review/release/commit/push/fetch back all exact artifacts. This file
does not embed an unknown future HEAD or self-referential registration digest.
Only fixed readonly Git tooling precedes the one finite cohort function call.
No external timeout, daemon, supervisor, fixture canary or retry exists.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types

HERE = Path(__file__).resolve().parent
EX = HERE.parent
FW = HERE.parents[5]
RAW = Path("/workspace/dtc-evidence-closure-20261019-v1/sem1/fixture-runtime-v1")
OUTPUT = RAW / "attempt1"
ENTRY_OUTPUT = RAW / "attempt1-entry"
PUBLICATION = RAW / "attempt1-prereg/PUBLICATION_READBACK.json"
BRANCH = "hrl/iscas2027-dtc-closure-exec-174-v1"
READBACK = "refs/dtc-closure-readback/sem1-fixture-runtime-v1"
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
NAMES = {
    "registration": "SEM1_FIXTURE_RUNTIME_REGISTRATION_V1.json",
    "release": "SEM1_FIXTURE_RUNTIME_RELEASE_V1.json",
    "policy": "SEM1_FIXTURE_RUNTIME_POLICY_V1.json",
    "roles": "SEM1_FIXTURE_RUNTIME_ROLES_V1.json",
    "manager": "SEM1_FIXTURE_RUNTIME_MANAGER_ROLE_V1.json",
    "abi": "SEM1_FIXTURE_ABI_FREEZE_V1.json",
}
RUNTIME_SHA = "56b3cdb367dd19d3a48a44a431ecd4ea579880d75d8ef4f61d9b3ab692f6cced"
CLASSIFIER_SHA = "e58caa464124703d65e8d2bd88c6108a2376ef8a01c48b6db8e49273be5a0b61"
PYTHON_SHA = "d6bca2b84e73c7775a0dd5e6a76899cfe4ee62863d7c8f88513811d1fda23f49"
GIT_SHA = "587ef21868c948b883993e23209b86a72a6ddc06aab1545c697ffc31075acd4a"
STATIC_PINS = {
    "STATIC_FREEZE.json": "73e56e269554a403825a10a4be51406099a49f9768f558e8f98a19d677fb314b",
    "COMPILE_RECIPES.json": "ae1c5b64c4a17414f2d3eb25e185c784c13d0a22d823e897708395a36b9ae7ec",
    "CORE_SOURCE_MANIFEST.json": "ce912464588d6ecf75e89bd20a4d2019df0d8aab0c374e28b69342be5b849f02",
    "MAPPING_MANIFESTS.json": "6d9fa7cc0f938708ec03364cea46edddeae15b947a890b6de2bb7d11edf0abe6",
    "STATIC_ELF_DEPENDENCIES.json": "33a1593ba20c8241cf3fce904cd72ecfe6db2bdcdc99569177b7f7e16219fd96",
    "READELF_NOTES.json": "7039c776230fceb2c067b84a8caaa38eb16f4bfd6f667f77e7b618a2fc5c892d",
}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                         separators=(",", ":")).encode()).hexdigest()


def write_new(path, value):
    data = (json.dumps(value, indent=2) + "\n").encode()
    require(len(data) <= 1024**2, "OUTER_RECEIPT_ONE_MiB_BOUND")
    with Path(path).open("xb") as stream:
        stream.write(data)


def publication(deadline):
    """Readonly bounded bootstrap; no target or resource sample."""
    def git(*args):
        left = deadline - time.monotonic()
        require(left > 0, "PUBLICATION_BOOTSTRAP_60S_BOUND")
        return subprocess.check_output(
            ["/usr/bin/git", "--no-optional-locks", "-C", str(FW),
             "-c", "core.fsmonitor=false", *args], env=ENV, text=True,
            timeout=min(15, left)).strip()
    require(sha("/usr/bin/git") == GIT_SHA, "PUBLISHED_GIT_TOOL_CHANGED")
    receipt = json.loads(PUBLICATION.read_text())
    head, tree = receipt["head"], receipt["tree"]
    require(receipt["status"] == "PUSHED_FETCHED_EXACT_CLEAN_SEM1_FIXTURE_RUNTIME" and
            isinstance(head, str) and len(head) == 40 and
            isinstance(tree, str) and len(tree) == 40 and
            receipt["fetched_head"] == head and receipt["fetched_tree"] == tree and
            receipt["branch"] == BRANCH, "FINAL_ACTUAL_PUBLICATION_READBACK_REQUIRED")
    require(git("rev-parse", "HEAD") == head == git("rev-parse", READBACK) and
            git("rev-parse", "HEAD^{tree}") == tree ==
            git("rev-parse", READBACK + "^{tree}") and
            not git("status", "--porcelain"), "EXACT_CLEAN_REMOTE_READBACK_HEAD_TREE")
    require(git("ls-remote", "--exit-code", "origin", "refs/heads/" + BRANCH).splitlines()
            == [head + "\trefs/heads/" + BRANCH], "REMOTE_BRANCH_CHANGED")
    files = receipt["files"]
    require(isinstance(files, dict) and files, "PUBLISHED_FILE_INDEX_REQUIRED")
    for relative, binding in files.items():
        require(time.monotonic() < deadline, "PUBLICATION_BOOTSTRAP_60S_BOUND")
        path = (FW / relative).resolve()
        require(not Path(relative).is_absolute() and path.is_relative_to(FW) and
                sha(path) == binding["sha256"] and
                git("rev-parse", head + ":" + relative) == binding["blob"],
                "PUBLISHED_SOURCE_BLOB_CHANGED:" + relative)
    paths = {key: EX / name for key, name in NAMES.items()}
    def published_sha(path):
        return files[str(path.relative_to(FW))]["sha256"]
    for path in paths.values():
        published_sha(path)  # required membership, never filename-only trust
    runtime = HERE / "bounded_fixture_runtime.py"
    classifier = HERE / "evaluate_fixture_output.py"
    for path, expected in ((runtime, RUNTIME_SHA), (classifier, CLASSIFIER_SHA)):
        require(published_sha(path) == expected, "EXACT_RUNTIME_CLASSIFIER_COPY_REQUIRED")
    require(str(Path(__file__).resolve().relative_to(FW)) in files,
            "OUTER_ENTRY_SOURCE_NOT_PUBLISHED")
    for name, expected in STATIC_PINS.items():
        require(published_sha(EX / "sem1_fixture_static_intake_v1" / name) == expected,
                "PARENT_STATIC_INTAKE_CHANGED:" + name)
    reg = json.loads(paths["registration"].read_text())
    role = json.loads(paths["manager"].read_text())
    require(reg["output"] == str(OUTPUT) and
            reg["release_path"] == str(paths["release"]) and
            reg["policy_path"] == str(paths["policy"]) and
            reg["roles_path"] == str(paths["roles"]) and
            reg["abi_freeze_path"] == str(paths["abi"]) and
            reg["abi_freeze_sha256"] == published_sha(paths["abi"]) and
            reg["classifier_path"] == str(classifier), "FIXED_PARENT_ARTIFACT_PATHS_REQUIRED")
    for path, expected in reg["source_sha256"].items():
        require(time.monotonic() < deadline, "PUBLICATION_BOOTSTRAP_60S_BOUND")
        absolute = Path(path)
        require(absolute.is_absolute() and sha(absolute) == expected,
                "FROZEN_COHORT_SOURCE_CHANGED:" + path)
        if absolute.is_relative_to(FW):
            require(published_sha(absolute) == expected,
                    "PARENT_SOURCE_NOT_IN_PUBLICATION:" + path)
    require(role["name"] == "SEM1_ACTUAL_OBJECT_FIXTURE_MANAGER_V1" and
            role["executable"] == "/usr/bin/python3.10" and
            role["executable_sha256"] == PYTHON_SHA and
            role["argvs"] == [["/usr/bin/python3.10", "-I", "-B",
                               str(HERE / "run_sem1_fixture_runtime_v1.py")]] and
            role["cwd"] == str(FW) and role["source_sha256"] == reg["source_sha256"],
            "EXACT_NEW_PARENT_ENTRY_ROLE_REQUIRED")
    trust = {key + "_sha256": published_sha(paths[key])
             for key in ("release", "policy", "roles")}
    trust["manager_role_sha256"] = canonical(role)
    return paths, reg, role, trust, published_sha(paths["registration"]), receipt


def main():
    require(HERE.name == "prepared_sem1_fixture_runtime_v1" and
            sys.argv == [str(HERE / "run_sem1_fixture_runtime_v1.py")] and
            Path.cwd() == FW and dict(os.environ) == ENV and
            sys.flags.isolated and sys.dont_write_bytecode and
            os.path.realpath(sys.executable) == os.path.realpath("/usr/bin/python3.10") and
            sha("/usr/bin/python3.10") == PYTHON_SHA,
            "EXACT_PARENT_FOREGROUND_ENTRY_ONLY")
    report, error, created = None, None, False
    calls = 0
    try:
        paths, reg, role, trust, reg_sha, published = publication(time.monotonic() + 60)
        RAW.mkdir(parents=True, exist_ok=True)
        ENTRY_OUTPUT.mkdir(exist_ok=False)
        created = True
        write_new(ENTRY_OUTPUT / "ENTRY_START.json", {
            "pid": os.getpid(), "argv": sys.argv, "cwd": str(FW),
            "publication_head": published["head"], "publication_tree": published["tree"],
            "registration_sha256": reg_sha, "trusted": trust, "cohort_call_limit": 1,
            "simulator_starts": 0, "native": "UNPROVEN"})
        engine = EX / "prepared_runtime"
        sys.path.insert(0, str(engine / "vendor"))
        sys.path.insert(0, str(engine))
        data = (HERE / "bounded_fixture_runtime.py").read_bytes()
        require(hashlib.sha256(data).hexdigest() == RUNTIME_SHA,
                "RUNTIME_SOURCE_CHANGED_BEFORE_IMPORT")
        module = types.ModuleType("_sem1_parent_exact_runtime")
        module.__file__ = str(HERE / "bounded_fixture_runtime.py")
        exec(compile(data, module.__file__, "exec"), module.__dict__)
        calls += 1
        report = module.run_exact_fixture_cohort(
            paths["registration"], reg_sha, trusted_hashes=trust, manager_role=role)
    except BaseException as failure:
        error = repr(failure)
    finally:
        if created:
            write_new(ENTRY_OUTPUT / "ENTRY_TERMINAL.json", {
                "error": error, "report": report, "cohort_calls": calls,
                "new_supervisor_or_guard": False, "external_timeout": False,
                "automatic_retry": False, "simulator_starts": 0,
                "native": "UNPROVEN", "architectural_values": "UNPROVEN"})
    print(json.dumps({"status": report["status"] if report else "STOP_OUTER_ENTRY",
                      "error": error, "cohort_calls": calls, "simulator_starts": 0}), flush=True)
    return 0 if error is None and report and report["status"] ==         "COMPLETE_CONDITIONAL_FIXTURE_COHORT_ONLY" else 3


if __name__ == "__main__":
    sys.exit(main())
