"""Short-Collect native authority adapter. Importing this module is inert.

All R0 tests use a private temporary registry. Live writes require an exact,
independently reviewed R0 release; no old Oracle request is accepted here.
"""
from __future__ import annotations

import copy
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time
import uuid

CONTRACT = "dfd6d7aa0383b8fda9ff08672f8c9efc392df26f"
CORE = "9a0de9b9f97144f481b3e3637e329ebab01acb74"
FRAMEWORK = "02775fd795cde5aae1480d81cee6eb481d0a08f4"
BINARY = "a9ec6f231d9491690eb913d1cb69d7d2dae0f769f8854efc4df0512b5f1fd00c"
LIB = "43b3dc2f3e04d577e6c682f632691aca637b2670aee52c18b809f4d4c4e64860"
STAGES = {
    "C1": ("GESUMMV", "vectorAdd"),
    "C2": ("MVT", "ATAX", "BICG", "scan", "3MM", "GEMM", "myocyte", "srad_v1"),
}
INPUTS = {
    "GESUMMV": "769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4",
    "vectorAdd": "e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799",
    "MVT": "f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079",
    "ATAX": "eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950",
    "BICG": "ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef",
    "scan": "6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39",
    "3MM": "977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d",
    "GEMM": "fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318",
    "myocyte": "977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992",
    "srad_v1": "0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4",
}


class Hold(RuntimeError):
    """Fail closed; a consumed identity is never retried or refunded."""


def need(condition, reason):
    if not condition:
        raise Hold(reason)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def encoded(obj):
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()


def write_exclusive(path, payload):
    path = Path(path)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    fsync_dir(path.parent)


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def replace_json(path, obj):
    path = Path(path)
    tmp = path.with_name("." + path.name + "." + str(os.getpid()) + ".writing")
    write_exclusive(tmp, encoded(obj))
    os.replace(tmp, path)
    fsync_dir(path.parent)


def request_cells(request):
    stage = request.get("stage")
    need(stage in STAGES, "UNKNOWN_STAGE")
    expected = {(program, mode) for program in STAGES[stage] for mode in ("OFF", "ON")}
    cells = request.get("cells")
    need(isinstance(cells, list) and len(cells) == len(expected), "EXACT_CELL_COUNT")
    actual = {(row.get("program"), row.get("mode")) for row in cells}
    need(actual == expected and len(actual) == len(cells), "EXACT_PROGRAM_MODE_MATRIX")
    return cells


def validate_request(request_path, root):
    root = Path(root).resolve()
    request_path = Path(request_path).resolve()
    need(request_path.is_relative_to(root), "REQUEST_OUTSIDE_ISOLATED_ROOT")
    request = read(request_path)
    need(request.get("contract_commit") == CONTRACT, "CONTRACT_DRIFT")
    need(request.get("candidate_core") == CORE and request.get("framework_commit") == FRAMEWORK,
         "FROZEN_SOURCE_DRIFT")
    need(request.get("binary_sha256") == BINARY and request.get("libcudart_sha256") == LIB,
         "FROZEN_RUNTIME_DRIFT")
    stage = request.get("stage")
    cells = request_cells(request)
    need(request.get("budget") == len(cells), "BUDGET_MISMATCH")
    request_id = request.get("request_id")
    need(isinstance(request_id, str) and request_id.startswith("DTC_SHORT_COLLECT_" + stage + "_"),
         "NEW_EXACT_REQUEST_ID_REQUIRED")
    need(request_id not in ("DTC_ORACLE_REMAINING24_20261106_V1", "DTC_ORACLE_INITIAL8_20261106_V1"),
         "OLD_ORACLE_ID_FORBIDDEN")
    specs = request.get("admitted_specs")
    need(isinstance(specs, dict) and len(specs) == len(cells), "EXACT_ADMITTED_SPECS")
    need(isinstance(request.get("plan_sha256"), str) and len(request["plan_sha256"]) == 64,
         "PLAN_SHA_REQUIRED")
    plan_path = (root / request.get("plan_path", "")).resolve()
    need(plan_path.is_relative_to(root) and plan_path.is_file() and
         sha(plan_path) == request["plan_sha256"], "EXACT_PLAN_FILE_SHA_REQUIRED")
    plan = read(plan_path)
    for key in ("contract_commit", "candidate_core", "framework_commit",
                "binary_sha256", "libcudart_sha256", "stage", "budget",
                "request_id", "reserved_write_bytes", "runtime_sha256",
                "source_pins_sha256"):
        need(plan.get(key) == request.get(key), "PLAN_REQUEST_DRIFT:" + key)
    source_pins = (root / plan.get("source_pins_path", "")).resolve()
    runtime_binding = (root / plan.get("runtime_binding_path", "")).resolve()
    need(source_pins.is_relative_to(root) and source_pins.is_file() and
         sha(source_pins) == request.get("source_pins_sha256"), "SOURCE_PINS_SHA_DRIFT")
    need(runtime_binding.is_relative_to(root) and runtime_binding.is_file() and
         sha(runtime_binding) == request.get("runtime_sha256"), "RUNTIME_BINDING_SHA_DRIFT")
    plan_cells = plan.get("cells")
    need(isinstance(plan_cells, list) and len(plan_cells) == len(cells),
         "PLAN_CELL_COUNT_DRIFT")
    plan_by_cohort = {row.get("cohort"): row for row in plan_cells}
    need(len(plan_by_cohort) == len(cells), "PLAN_DUPLICATE_COHORT")
    need(type(request.get("reserved_write_bytes")) is int and request["reserved_write_bytes"] > 0,
         "BOUNDED_WRITE_RESERVATION_REQUIRED")
    cohorts = set()
    for row in cells:
        program, mode, cohort = row["program"], row["mode"], row["cohort"]
        need(row.get("input_sha256") == INPUTS[program], "INPUT_SHA_DRIFT")
        need(isinstance(cohort, str) and cohort.startswith("E2-DTCSHORT-" + stage + "-")
             and cohort not in cohorts, "EXACT_NEW_COHORT_REQUIRED")
        cohorts.add(cohort)
        spec_path = (root / row["spec_path"]).resolve()
        need(spec_path.is_relative_to(root) and spec_path.is_file(), "SPEC_PATH_OR_FILE")
        digest = sha(spec_path)
        need(row.get("spec_sha256") == specs.get(cohort) == digest, "SPEC_SHA_DRIFT")
        spec = read(spec_path)
        planned = plan_by_cohort.get(cohort)
        need(isinstance(planned, dict), "PLAN_MISSING_COHORT")
        for key in ("cohort", "program", "mode", "input_sha256", "spec_path", "spec_sha256"):
            need(planned.get(key) == row.get(key), "PLAN_CELL_REQUEST_DRIFT:" + key)
        need(planned.get("host_cpu") == spec.get("host_cpu") and
             planned.get("expected") == spec.get("expected") and
             planned.get("trace_kernelslist_sha256") == spec.get("trace_kernelslist_sha256"),
             "PLAN_CELL_SPEC_DRIFT")
        need(plan.get("limits_per_cell") == spec.get("limits"), "PLAN_LIMIT_SPEC_DRIFT")
        need(spec.get("request") == request_id and spec.get("cohort") == cohort
             and spec.get("program") == program and spec.get("mode") == mode
             and spec.get("input_sha256") == INPUTS[program], "SPEC_IDENTITY_DRIFT")
        need(spec.get("core_commit") == CORE and spec.get("framework_commit") == FRAMEWORK
             and spec.get("binary_sha256") == BINARY and spec.get("libcudart_sha256") == LIB,
             "SPEC_RUNTIME_DRIFT")
    need(set(specs) == cohorts, "SPEC_COHORT_SET_DRIFT")
    return request


def validate_release(release_path, request_path, engine_path, stage):
    release = read(release_path)
    need(release.get("status") == "R0_NATIVE_ROUTE_QUALIFIED", "R0_NOT_QUALIFIED")
    need(release.get("contract_commit") == CONTRACT, "R0_CONTRACT_DRIFT")
    need(release.get("request_sha256") == sha(request_path), "R0_REQUEST_DRIFT")
    need(release.get("engine_sha256") == sha(engine_path), "R0_ENGINE_DRIFT")
    need(release.get("independent_reviewer") and release.get("implementer")
         and release["independent_reviewer"] != release["implementer"], "INDEPENDENT_REVIEW_MISSING")
    if stage == "C2":
        gate = release.get("c1_gate")
        need(isinstance(gate, dict) and gate.get("status") == "C1_STRICT_ARCHIVE_RESTORE_REVIEW_PASS"
             and gate.get("accepted_cells") == 4
             and isinstance(gate.get("gesummv_on_eligible_choice_different"), int)
             and gate["gesummv_on_eligible_choice_different"] > 0, "C1_GATE_NOT_OPEN")
    return release


class RegistryStore:
    """One EX writer, bounded SH reader, append-only request and identity semantics."""

    def __init__(self, registry, epoch, lock, *, fixture_only=True):
        self.registry, self.epoch, self.lock = map(Path, (registry, epoch, lock))
        self.fixture_only = fixture_only

    def _lock(self, mode, timeout=2.0):
        handle = self.lock.open("r+b")
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(handle, mode | fcntl.LOCK_NB)
                return handle
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    handle.close()
                    raise Hold("REGISTRY_LOCK_BUSY_HOLD_NO_START")
                time.sleep(0.02)

    def _locked_snapshot(self):
        r, e = read(self.registry), read(self.epoch)
        need(e.get("epoch") == 2 and e.get("state") == "NATIVE_SCIENCE_ACTIVE",
             "NATIVE_EPOCH2_REQUIRED")
        need(e.get("native_registry_sha256") == sha(self.registry), "REGISTRY_EPOCH_SHA_MISMATCH")
        return r, e

    def snapshot(self):
        with self._lock(fcntl.LOCK_SH):
            return self._locked_snapshot()

    def _write_locked(self, before, epoch, after, request_id, operation):
        old = before["registered_future_requests"]
        new = after["registered_future_requests"]
        need(set(old) <= set(new) and set(new) - set(old) <= {request_id}, "REQUEST_HISTORY_MUTATION")
        need(all(new[k] == v for k, v in old.items() if k != request_id), "FOREIGN_REQUEST_MUTATION")
        immutable = lambda x: {k: v for k, v in x.items()
                               if k not in ("registered_future_requests", "new_scientific_budget_remaining")}
        need(immutable(before) == immutable(after), "FOREIGN_REGISTRY_MUTATION")
        q = new[request_id]
        need(q["remaining"] == q["budget"] - len(q["consumed"]), "BUDGET_CONSERVATION")
        need(set(q["consumed"]) <= set(q["admitted_specs"]), "UNADMITTED_CONSUMPTION")
        need(len({v["uuid"] for v in q["consumed"].values()}) == len(q["consumed"]), "UUID_DUPLICATION")
        if request_id in old:
            prev = old[request_id]
            need(q["budget"] == prev["budget"] and q["admitted_specs"] == prev["admitted_specs"],
                 "BUDGET_OR_SPEC_REWRITE")
            need(set(prev["consumed"]) <= set(q["consumed"]), "CONSUMED_REFUND")
            for cohort, row in prev["consumed"].items():
                need(all(q["consumed"][cohort].get(k) == v for k, v in row.items()),
                     "CONSUMED_IDENTITY_REWRITE")
        after["new_scientific_budget_remaining"] = sum(
            row.get("remaining", max(0, row.get("budget", 0) -
                                    (row.get("consumed", 0) if isinstance(row.get("consumed", 0), int)
                                     else len(row.get("consumed", {})))))
            for row in new.values())
        history = self.registry.parent / "request_history"
        history.mkdir(exist_ok=True)
        for path in (self.registry, self.epoch):
            backup = history / (path.stem + "." + sha(path) + ".json")
            if not backup.exists():
                write_exclusive(backup, path.read_bytes())
        prior_r, prior_e = sha(self.registry), sha(self.epoch)
        replace_json(self.registry, after)
        updated = copy.deepcopy(epoch)
        updated["native_registry_sha256"] = sha(self.registry)
        updated["new_budget_remaining"] = after["new_scientific_budget_remaining"]
        updated["request_revision"] = {
            "request_id": request_id, "operation": operation,
            "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "prior_registry_sha256": prior_r, "prior_current_epoch_sha256": prior_e,
        }
        replace_json(self.epoch, updated)

    def register(self, request_path, root, engine_path, *, release_path=None):
        request = validate_request(request_path, root)
        if not self.fixture_only:
            need(release_path is not None, "LIVE_R0_RELEASE_REQUIRED")
            validate_release(release_path, request_path, engine_path, request["stage"])
        request_id = request["request_id"]
        with self._lock(fcntl.LOCK_EX):
            before, epoch = self._locked_snapshot()
            need(request_id not in before["registered_future_requests"], "REQUEST_ALREADY_REGISTERED")
            after = copy.deepcopy(before)
            after["registered_future_requests"][request_id] = {
                "request": request_id, "state": "ARMED", "budget": request["budget"],
                "remaining": request["budget"], "admitted_specs": request["admitted_specs"],
                "consumed": {}, "spec_request_sha256": sha(request_path),
                "engine_sha256": sha(engine_path), "plan_sha256": request["plan_sha256"],
                "model_automatic_retries": 0, "reserved_write_bytes": request["reserved_write_bytes"],
                "contract_commit": CONTRACT, "stage": request["stage"],
            }
            self._write_locked(before, epoch, after, request_id, "SHORT_COLLECT_REGISTER")
        return {"status": "REGISTERED", "request": request_id, "budget": request["budget"]}

    def consume(self, request_path, root, cohort, ledger_dir, output_root, *,
                lease_check, preflight_check, locked_admission_check,
                uuid_factory=uuid.uuid4):
        """Charge one exact identity before any launcher fork.

        A durable INTENT can precede a crash before registry commit. This is
        HOLD requiring forward reconciliation; the identity is never retried.
        The locked callback sees the passed registry snapshot. It must not call
        snapshot() or any other SH authority reader while EX is held.
        """
        request = validate_request(request_path, root)
        request_id = request["request_id"]
        need(cohort in request["admitted_specs"], "UNREGISTERED_CELL")
        lease_check()
        preflight_check()
        ledger_dir, output_root = Path(ledger_dir), Path(output_root)
        need(ledger_dir.is_dir() and output_root.is_dir(), "LEDGER_OR_OUTPUT_ROOT_MISSING")
        intent_path = ledger_dir / (cohort + ".INTENT.json")
        with self._lock(fcntl.LOCK_EX):
            before, epoch = self._locked_snapshot()
            q = before["registered_future_requests"].get(request_id)
            need(q is not None and q["spec_request_sha256"] == sha(request_path),
                 "REQUEST_NOT_REGISTERED_OR_DRIFT")
            need(q["state"] in ("ARMED", "RUNNING") and q["remaining"] > 0
                 and cohort not in q["consumed"], "CELL_CONSUMED_OR_SEALED")
            need(not intent_path.exists(), "INTENT_ALREADY_EXISTS_NO_RETRY")
            need(q["admitted_specs"] == request["admitted_specs"], "ADMITTED_SPEC_DRIFT")
            cell = next(row for row in request["cells"] if row["cohort"] == cohort)
            spec_path = (Path(root).resolve() / cell["spec_path"]).resolve()
            need(spec_path.is_relative_to(Path(root).resolve()) and
                 sha(spec_path) == cell["spec_sha256"] == q["admitted_specs"][cohort],
                 "LOCKED_SPEC_BYTES_DRIFT")
            locked_admission_check(before, q)
            # All potentially blocking checks were completed before EX. Callbacks
            # must not recurse through snapshot() while this EX is held.
            identity = str(uuid_factory())
            need(uuid.UUID(identity).version == 4, "RANDOM_UUID4_REQUIRED")
            need(all(row["uuid"] != identity for req in before["registered_future_requests"].values()
                     if isinstance(req.get("consumed"), dict) for row in req["consumed"].values()),
                 "UUID_REUSE")
            output = output_root / identity
            output.mkdir(mode=0o700)
            intent = {
                "request": request_id, "cohort": cohort, "uuid": identity,
                "spec_sha256": request["admitted_specs"][cohort],
                "request_sha256": sha(request_path), "output": str(output.resolve()),
                "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "charged": 1, "consumed_before_launcher_fork": 1,
                "automatic_retry": False,
            }
            write_exclusive(intent_path, encoded(intent))
            after = copy.deepcopy(before)
            own = after["registered_future_requests"][request_id]
            own["consumed"][cohort] = {
                "uuid": identity, "intent": str(intent_path.resolve()),
                "intent_sha256": sha(intent_path), "charged": 1,
            }
            own["remaining"] -= 1
            own["state"] = "RUNNING"
            self._write_locked(before, epoch, after, request_id, "SHORT_COLLECT_CONSUME")
        return intent

    def append_receipt(self, request_id, cohort, receipt_path):
        receipt = read(receipt_path)
        with self._lock(fcntl.LOCK_EX):
            before, epoch = self._locked_snapshot()
            q = before["registered_future_requests"].get(request_id)
            need(q is not None and cohort in q["consumed"], "UNCONSUMED_RECEIPT")
            need(receipt.get("request") == request_id and receipt.get("cohort") == cohort
                 and receipt.get("uuid") == q["consumed"][cohort]["uuid"], "RECEIPT_IDENTITY_DRIFT")
            need("execution_receipt" not in q["consumed"][cohort], "RECEIPT_ALREADY_ATTACHED")
            after = copy.deepcopy(before)
            after["registered_future_requests"][request_id]["consumed"][cohort]["execution_receipt"] = {
                "path": str(Path(receipt_path).resolve()), "sha256": sha(receipt_path),
            }
            self._write_locked(before, epoch, after, request_id, "SHORT_COLLECT_RECEIPT")
        return {"status": "RECEIPT_ATTACHED", "request": request_id, "cohort": cohort}
