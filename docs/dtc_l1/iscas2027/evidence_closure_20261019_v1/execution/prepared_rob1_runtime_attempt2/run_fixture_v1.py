"""SOURCE_PREPARED_NOT_EXECUTED: parent-only ROB1 six-case outer entry.

Copy unchanged into execution/prepared_rob1_runtime. No outer timer, fixture
Popen, model/guard API or retry. The frozen ROB1 cohort exclusively owns its
600s bound, six exact fixture launches, six fresh admissions and own cleanup.
Only fixed read-only Git tooling children are created by this outer module.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


HERE = Path(__file__).resolve().parent
EX = HERE.parent
FW = HERE.parents[5]
ENGINE = EX / "prepared_runtime"
REGISTRATION = EX / "ROB1_FIXTURE_RUNTIME_REGISTRATION_ATTEMPT2.json"
STATIC = EX / "rob1_fixture_static_intake_v1/STATIC_FREEZE.json"
OUTER = Path("/workspace/dtc-evidence-closure-20261019-v1/coordinator/rob1-fixture-runtime-v1-attempt2")
PUBLICATION = OUTER.parent / "rob1-fixture-runtime-v1-attempt2-prereg/PUBLICATION_READBACK.json"
INNER = "/workspace/dtc-evidence-closure-20261019-v1/rob1/fixture-runtime-v1/attempt2"
READBACK = "refs/dtc-closure-readback/rob1-fixture-runtime-v1-attempt2"
BRANCH = "hrl/iscas2027-dtc-closure-exec-174-v1"
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
ORDER = ("omitted", "explicit_zero", "quota_one", "bad_width", "bad_mode", "nonfinite")
STATIC_SHA = "05a100bfa7fa2be0181fe32aeb59a68614501902c8db1fb20cff70317778dac7"
RUNTIME_SHA = "c73f30cd91a66f688c97de9177845eee88084a883124ff8cc6a88c5126cc95a9"
CLASSIFIER_SHA = "d5428e9114bbd3e6cf02670f1c1d664cc134bad572e42dd26ec928f75a70fcd2"
ELF_SHA = "978b6e605f045808ee410e3b8d51934b74a621e17614a6f7f50a872aef2b9312"
LIB_SHA = "22963c70368489f930ae73a2383520d1da30996c6503fe565b5edd5c3770faf1"
OUTER_BOUND = 1024**2


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for data in iter(lambda: stream.read(65536), b""):
            digest.update(data)
    return digest.hexdigest()


def git(*arguments):
    return subprocess.check_output(["/usr/bin/git", "--no-optional-locks", "-C", str(FW),
        "-c", "core.fsmonitor=false", *arguments], env=ENV, text=True, timeout=10).strip()


def publication():
    receipt = json.loads(PUBLICATION.read_bytes())
    head, tree = receipt["head"], receipt["tree"]
    require(receipt["fetched_head"] == head and receipt["fetched_tree"] == tree and receipt["branch"] == BRANCH,
            "EXACT_REMOTE_READBACK_REQUIRED")
    require(git("rev-parse", "HEAD") == head == git("rev-parse", READBACK) and
            git("rev-parse", "HEAD^{tree}") == tree == git("rev-parse", READBACK + "^{tree}") and
            not git("status", "--porcelain"), "EXACT_CLEAN_HEAD_TREE_REQUIRED")
    require(git("ls-remote", "--exit-code", "origin", "refs/heads/" + BRANCH).splitlines() ==
            [head + "\trefs/heads/" + BRANCH], "REMOTE_RUNTIME_RELEASE_CHANGED")
    require(1 <= len(receipt["files"]) <= 128, "FINITE_PUBLISHED_FILE_SET_REQUIRED")
    for relative, item in receipt["files"].items():
        path = (FW / relative).resolve()
        require(path.is_relative_to(FW) and sha(path) == item["sha256"] and
                git("rev-parse", head + ":" + relative) == item["blob"],
                "PUBLISHED_RUNTIME_BYTES_OR_BLOB_CHANGED:" + relative)
    for required in (REGISTRATION, STATIC, HERE / "run_fixture_v1.py"):
        require(str(required.relative_to(FW)) in receipt["files"], "REQUIRED_RUNTIME_RELEASE_FILE_NOT_PUBLISHED")
    registration = json.loads(REGISTRATION.read_bytes())
    require(registration["status"] == "RELEASED_ROB1_SIX_ACTUAL_LDST_CPU_CASES_ONLY" and
            registration["ordered_cases"] == list(ORDER) and registration["output"] == INNER and
            registration["admission"]["disk_floor_exclusive_bytes"] == 5 * 1024**3 and
            registration["timeout_seconds"] == 600 and registration["maximum_fixture_launches"] == 6 and
            registration["concurrency"] == 1 and registration["retries"] == 0 and
            registration["simulator_starts"] == 0, "EXACT_SIX_CASE_COHORT_RELEASE_REQUIRED")
    sources = registration["source_sha256"]
    require(len(json.dumps(sources).encode()) <= 64 * 1024, "COMPACT_COMPLETE_SOURCE_BINDING_REQUIRED")
    parent_sources = registration["parent_engine_source_sha256"]
    own_sources = {str(HERE / name) for name in ("run_fixture_v1.py", "finite_ldst_runtime.py",
                                               "evaluate_fixture_output.py")}
    require(type(parent_sources) is dict and len(parent_sources) == 39 and
            set(sources) == own_sources | {str(ENGINE / relative) for relative in parent_sources} and
            all(sources[str(ENGINE / relative)] == expected for relative, expected in parent_sources.items()),
            "UNCHANGED_PARENT_39_PLUS_THREE_ENTRY_SOURCES_REQUIRED")
    required = (HERE / "run_fixture_v1.py", HERE / "finite_ldst_runtime.py",
                HERE / "evaluate_fixture_output.py", ENGINE / "cpu_admission_v2.py",
                ENGINE / "shared_authority.py", ENGINE / "vendor/ownership.py")
    require(set(map(str, required)) <= set(sources), "RUNTIME_AND_PARENT_GATE_CLOSURE_REQUIRED")
    for absolute, expected in sources.items():
        path = Path(absolute).resolve()
        require(path.is_relative_to(FW), "SOURCE_NOT_IN_PARENT_FRAMEWORK")
        relative = str(path.relative_to(FW))
        require(relative in receipt["files"] and receipt["files"][relative]["sha256"] == expected and
                sha(path) == expected, "SOURCE_NOT_BOUND_TO_PUBLISHED_RELEASE:" + absolute)
    require(sources[str(HERE / "finite_ldst_runtime.py")] == RUNTIME_SHA and
            sources[str(HERE / "evaluate_fixture_output.py")] == CLASSIFIER_SHA,
            "UNCHANGED_ROB0E0EBF_RUNTIME_AND_CLASSIFIER_REQUIRED")
    role = registration["runtime_role"]
    require(role["name"] == "ROB1_ACTUAL_LDST_FIXTURE_RUNTIME_CONTROL" and
            role["argvs"] == [["/usr/bin/python3.10", "-I", "-B", str(HERE / "run_fixture_v1.py")]] and
            role["cwd"] == str(FW) and role["executable"] == "/usr/bin/python3.10" and
            sha(role["executable"]) == role["executable_sha256"] and role["source_sha256"] == sources,
            "ACTUAL_SOURCE_BOUND_DISTINCT_RUNTIME_ROLE_REQUIRED")
    require(registration["static_freeze"] == dict(path=str(STATIC), sha256=STATIC_SHA) and
            sha(STATIC) == STATIC_SHA, "EXACT_ACTUAL_STATIC_FREEZE_REQUIRED")
    frozen = json.loads(STATIC.read_bytes())
    require(frozen["core_commit"] == "b1077667f7a2bcc72260733f88f5798f167346d1" and
            frozen["core_tree"] == "0a462efb9a48409064259735108b88dad127a53c" and
            frozen["fixture_sha256"] == ELF_SHA and frozen["library_sha256"] == LIB_SHA,
            "ACTUAL_MATCHING_B107_ELF_LIBRARY_STATIC_INTAKE_REQUIRED")
    return registration, receipt


def module_binding(module, path, sources):
    require(Path(module.__file__).resolve() == path.resolve() and sha(path) == sources[str(path)],
            "ACTUAL_IMPORTED_SOURCE_CHANGED:" + str(path))


def main():
    require(HERE.name == "prepared_rob1_runtime_attempt2" and sys.argv == [str(HERE / "run_fixture_v1.py")] and
            Path.cwd() == FW and dict(os.environ) == ENV and sys.flags.isolated and
            sys.flags.dont_write_bytecode, "EXACT_PARENT_FOREGROUND_RUNTIME_ENTRY_REQUIRED")
    OUTER.mkdir(parents=True, exist_ok=False)
    written = 0
    def write(name, value):
        nonlocal written
        data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
        limit = OUTER_BOUND if name == "ENTRY_TERMINAL.json" else OUTER_BOUND - 128 * 1024
        require(written + len(data) <= limit, "OUTER_COMPACT_RECEIPT_BOUND")
        with (OUTER / name).open("xb") as stream:
            stream.write(data)
        written += len(data)
    result = None
    failure = None
    calls = 0
    binding = {}
    try:
        write("ENTRY_START.json", dict(utc=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
            argv=sys.argv, cwd=str(FW), run_registered_calls=0, simulator_starts=0,
            scope="PARENT_ROB1_CPU_RUNTIME_ONLY_NO_OUTER_TIMER_OR_SUPERVISOR"))
        registration, published = publication()
        registration_sha = sha(REGISTRATION)
        binding = dict(registration_sha256=registration_sha, publication_sha256=sha(PUBLICATION),
            publication_head=published["head"], publication_tree=published["tree"],
            source_sha256=registration["source_sha256"], static_freeze_sha256=STATIC_SHA,
            fixture_sha256=ELF_SHA, library_sha256=LIB_SHA)
        write("SOURCE_PUBLICATION_BINDING.json", dict(binding, clean=True, remote_branch=BRANCH,
              readback_ref=READBACK, source_scope="ROB0E0EBF_PLUS_UNCHANGED_PARENT_GATE_IMPORTS"))
        sys.path.insert(0, str(ENGINE / "vendor"))
        sys.path.insert(0, str(ENGINE))
        sys.path.insert(0, str(HERE))
        import cpu_admission_v2
        import finite_ldst_runtime
        import evaluate_fixture_output
        for module, path in ((cpu_admission_v2, ENGINE / "cpu_admission_v2.py"),
                             (finite_ldst_runtime, HERE / "finite_ldst_runtime.py"),
                             (evaluate_fixture_output, HERE / "evaluate_fixture_output.py")):
            module_binding(module, path, registration["source_sha256"])
        require(tuple(finite_ldst_runtime.ORDER) == ORDER and tuple(evaluate_fixture_output.CASES) == ORDER and
                finite_ldst_runtime.TOTAL_SECONDS == 600, "UNCHANGED_SIX_CASE_INTERNAL_TIMER_CONTRACT")
        calls = 1
        result = finite_ldst_runtime.run_registered(REGISTRATION, registration_sha,
            cpu_admission_class=cpu_admission_v2.CPUAdmission, classify_output=evaluate_fixture_output.classify)
        # No retry, second admission loop or post-run target call is added here.
        after_registration, after_publication = publication()
        require(after_registration == registration and after_publication == published and
                sha(REGISTRATION) == registration_sha, "RUNTIME_PUBLICATION_CHANGED_BEFORE_OUTER_TERMINAL")
        require(result["status"] == "PASS_SIX_ACTUAL_LDST_CPU_CASES_ONLY" and result["actual_starts"] == 6 and
                tuple(row["case"] for row in result["results"]) == ORDER and result["simulator_starts"] == 0 and
                all(row["classification"]["status"] == ("PASS_ACTUAL_LDST_COMPONENT_COMPLETION" if index < 3 else
                    "PASS_EXPECTED_ACTUAL_CTOR_REJECTION") for index, row in enumerate(result["results"])),
                "SIX_SCOPED_ACTUAL_RESULTS_NOT_COMPLETE")
    except BaseException as error:
        failure = repr(error)
    finally:
        write("ENTRY_TERMINAL.json", dict(utc=datetime.now(timezone.utc).isoformat(), error=failure,
            run_registered_calls=calls, report=result, binding=binding, simulator_starts=0,
            no_background_retry=True, whole_binary_OFF_equivalence=False, production_authority=False,
            status="PASS_PARENT_ROB1_SIX_CPU_CASE_ENTRY_ONLY" if failure is None and result is not None
            else "STOP_PARENT_ROB1_CPU_RUNTIME_ENTRY"))
    print(json.dumps(dict(status="PASS_PARENT_ROB1_SIX_CPU_CASE_ENTRY_ONLY" if failure is None else
        "STOP_PARENT_ROB1_CPU_RUNTIME_ENTRY", output=str(OUTER), run_registered_calls=calls,
        actual_fixture_starts=result["actual_starts"] if result else 0, simulator_starts=0)), flush=True)
    return 0 if failure is None and result is not None else 3


if __name__ == "__main__":
    sys.exit(main())
