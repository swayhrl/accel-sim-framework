"""PREPARED_NOT_TESTED: read-only admission of three exact external CPU roles.

Import only defines objects. Construction copies caller-pinned contracts; it
does not read files/processes, call providers or read a clock. observe() reads
only the injected registered sole-manager view, fresh process attributes and
registered file hashes. No process creation, signal, wait, ptrace, ownership
adoption, role discovery or registration-writing interface exists.

This module does not evaluate resource samples. Trusted admissions must come
from the coordinator's actual PASS receipts under its fixed policy hash. The
parent caller must bind the provider implementation in the manager's published
source closure; a JSON row alone cannot prove a direct Popen provenance.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
import time
from types import MappingProxyType


ROLE_NAMES = frozenset({
    "COV1_TINY_MATH_REFERENCE_FOUR_TESTS",
    "SEM1_BOUNDED_DIAGNOSTIC_BUILD_CONTROL",
    "ROB1_BOUNDED_DIAGNOSTIC_BUILD_CONTROL",
})
INSTANCE_FIELDS = ("boot_id", "pid", "start_ticks", "tgid")


class ExternalCPUReject(ValueError):
    """No external-role acceptance; caller preserves its ordinary stop policy."""


class _NotCurrent(Exception):
    def __init__(self, classification):
        self.classification = classification


def require(condition, reason):
    if not condition:
        raise ExternalCPUReject(reason)


def is_sha256(value):
    return (isinstance(value, str) and len(value) == 64 and
            all(char in "0123456789abcdef" for char in value))


def file_sha256(path):
    """Read only a caller-registered file, and only during observe()."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instance_key(record):
    return tuple(record[field] for field in INSTANCE_FIELDS)


class ExternalCPULaunchView:
    """Fixed trust + one source-bound sole-manager provider; no own registry.

    trusted keys: release_sha256, role_contract_sha256, admission_policy_sha256,
    manager_role_sha256, manager, roles. manager has instance and exact argv,
    cwd, executable, executable_sha256, source_sha256. Each role has the same
    exact fields except instance/argv, and phases maps phase -> {argv,
    max_runtime_ns, output_bound_bytes}. admissions maps role -> phase ->
    {receipt_sha256, policy_sha256, status='PASS', scope='CPU_ONLY',
    valid_from_monotonic_ns, valid_until_monotonic_ns}.

    provider() returns {manager_instance, manager_role_sha256, launches}. Its
    launch rows contain only actual direct-Popen records from that same fixed
    manager. It must not populate rows from /proc discovery or self-assertions.
    The example schema and integration constraints live beside this module.
    """
    def __init__(self, *, trusted, admissions, provider, identity_reader,
                 process_reader, monotonic_ns=time.monotonic_ns,
                 file_sha256_reader=file_sha256):
        self._trusted = deepcopy(trusted)
        self._admissions = deepcopy(admissions)
        self._provider = provider
        self._identity = identity_reader
        self._process = process_reader
        self._clock = monotonic_ns
        self._file_sha256 = file_sha256_reader
        require(bool(self._trusted["roles"]) and
                set(self._trusted["roles"]) <= ROLE_NAMES,
                "ONLY_THE_THREE_REGISTERED_CPU_ROLES")
        for field in ("release_sha256", "role_contract_sha256",
                      "admission_policy_sha256", "manager_role_sha256"):
            value = self._trusted[field]
            require(is_sha256(value),
                    "FIXED_TRUST_HASH_REQUIRED:" + field)

    def _fresh(self, expected, spec):
        """Bracket a full current process read; never trust the saved argv row."""
        key = instance_key(expected)
        def read(reader):
            try:
                row = reader(expected["pid"])
            except (FileNotFoundError, ProcessLookupError):
                raise _NotCurrent("NOT_CURRENT") from None
            if row is None:
                raise _NotCurrent("NOT_CURRENT")
            require(instance_key(row) == key, "CURRENT_PROCESS_INSTANCE_CHANGED")
            if row["state"] in ("Z", "X", "x"):
                raise _NotCurrent("TERMINAL")
            return row
        before = read(self._identity)
        current = read(self._process)
        after = read(self._identity)
        require(current["pid"] == current["tgid"], "CPU_CONTROL_MUST_BE_TGID_ROOT")
        require(current["argv"] == spec["argv"] and
                current["cwd"] == spec["cwd"] and
                current["exe"] == spec["executable"],
                "CURRENT_CPU_ATTRIBUTES_CHANGED")
        # These fields can change without changing PID/start_ticks. Compare
        # current attributes again after source hashing before returning.
        require(before["ppid"] == current["ppid"] == after["ppid"] and
                before["tracer_pid"] == current["tracer_pid"] == after["tracer_pid"],
                "CURRENT_PARENT_OR_TRACER_CHANGED")
        require(current["tracer_pid"] == spec.get("tracer_pid", 0),
                "CPU_CONTROL_TRACER_NOT_REGISTERED")
        return current

    def _hashes(self, spec):
        actual = self._file_sha256(spec["executable"])
        require(actual == spec["executable_sha256"], "CPU_EXECUTABLE_HASH_CHANGED")
        source = []
        require(bool(spec["source_sha256"]), "EMPTY_CPU_SOURCE_CLOSURE")
        for path, expected in sorted(spec["source_sha256"].items()):
            digest = self._file_sha256(path)
            require(digest == expected, "CPU_SOURCE_HASH_CHANGED:" + path)
            source.append((path, digest))
        return actual, tuple(source)

    def observe(self, role_name, candidate, *, callback_sample_id):
        """Return an immutable accepted row, or reject without altering anything.

        Call only after the parent finds an exact-role candidate. candidate
        supplies at least pid/start_ticks; all acceptance attributes are read
        afresh. Readers/providers are trusted source-bound injections, not row
        fields. Natural absence/exit returns NOT_CURRENT/TERMINAL, never live
        acceptance. Changed identities/contracts reject; cached START rows
        cannot be turned into live observations.
        dict(result) is JSON serializable; no ownership object is returned.
        """
        trust = self._trusted
        require(role_name in trust["roles"], "CPU_ROLE_NOT_REGISTERED")
        require(not candidate.get("is_simulator", False), "CPU_ROLE_CANNOT_BE_SIMULATOR")
        require(isinstance(callback_sample_id, str) and bool(callback_sample_id),
                "CALLBACK_SAMPLE_ID_REQUIRED")
        began = self._clock()
        launch = None
        try:
            snapshot = deepcopy(self._provider())
            manager = trust["manager"]
            manager_key = instance_key(manager["instance"])
            require(instance_key(snapshot["manager_instance"]) == manager_key and
                    snapshot["manager_role_sha256"] == trust["manager_role_sha256"],
                    "SOLE_MANAGER_REGISTRATION_CHANGED")
            rows = [row for row in snapshot["launches"]
                    if row["role_name"] == role_name and
                    row["instance"]["pid"] == candidate["pid"] and
                    row["instance"]["start_ticks"] == candidate["start_ticks"]]
            require(len(rows) == 1, "NO_UNIQUE_REGISTERED_DIRECT_LAUNCH")
            launch = rows[0]
            require(isinstance(launch["actual_launch_id"], str) and
                    bool(launch["actual_launch_id"]), "DIRECT_LAUNCH_ID_REQUIRED")
            require(instance_key(launch["manager_instance"]) == manager_key,
                    "EXTERNAL_LAUNCH_NOT_FROM_SOLE_MANAGER")
            for field in ("release_sha256", "role_contract_sha256",
                          "admission_policy_sha256"):
                require(launch[field] == trust[field], "EXTERNAL_BINDING_CHANGED:" + field)
            role = trust["roles"][role_name]
            phase_name = launch["phase"]
            require(phase_name in role["phases"], "CPU_PHASE_NOT_REGISTERED")
            phase = role["phases"][phase_name]
            spec = dict(role, argv=phase["argv"])
            require(launch["argv"] == phase["argv"] and
                    launch["cwd"] == role["cwd"] and
                    launch["executable"] == role["executable"],
                    "DIRECT_LAUNCH_ATTRIBUTES_CHANGED")
            admission = self._admissions[role_name][phase_name]
            require(is_sha256(admission["receipt_sha256"]) and
                    admission["status"] == "PASS" and admission["scope"] == "CPU_ONLY" and
                    admission["policy_sha256"] == trust["admission_policy_sha256"] and
                    launch["admission_sha256"] == admission["receipt_sha256"],
                    "EXTERNAL_ADMISSION_NOT_TRUSTED")
            started = launch["launched_monotonic_ns"]
            deadline = launch["deadline_monotonic_ns"]
            require(type(started) is int and type(deadline) is int and started >= 0 and
                    0 < deadline - started <= phase["max_runtime_ns"] and
                    admission["valid_from_monotonic_ns"] <= started and
                    deadline <= admission["valid_until_monotonic_ns"] and
                    launch["output_bound_bytes"] == phase["output_bound_bytes"],
                    "EXTERNAL_PHASE_BOUND_OR_ADMISSION_CHANGED")
            require(launch["state"] in ("ACTIVE", "TERMINAL_REAPED", "RETIRED"),
                    "EXTERNAL_LAUNCH_STATE_UNREGISTERED")
            if launch["state"] != "ACTIVE":
                raise _NotCurrent("TERMINAL")
            require(started <= began <= deadline, "EXTERNAL_PHASE_EXPIRED")
            first_manager = self._fresh(manager["instance"], manager)
            self._hashes(manager)
            current = self._fresh(launch["instance"], spec)
            require(current["ppid"] == manager["instance"]["pid"],
                    "CPU_CONTROL_NOT_DIRECT_MANAGER_CHILD")
            executable_hash, source_hashes = self._hashes(spec)
            final = self._fresh(launch["instance"], spec)
            final_manager = self._fresh(manager["instance"], manager)
            require(current["ppid"] == final["ppid"] and
                    current["tracer_pid"] == final["tracer_pid"] and
                    first_manager["ppid"] == final_manager["ppid"] and
                    first_manager["tracer_pid"] == final_manager["tracer_pid"],
                    "CPU_INSTANCE_CHANGED_DURING_HASH_READ")
            ended = self._clock()
            require(began <= ended <= deadline, "EXTERNAL_OBSERVATION_EXPIRED")
            return MappingProxyType({
                "classification": "EXACT_EXTERNAL_CPU_CONTROL_OBSERVED",
                "role_name": role_name, "phase": phase_name,
                "actual_launch_id": launch["actual_launch_id"],
                "release_sha256": trust["release_sha256"],
                "role_contract_sha256": trust["role_contract_sha256"],
                "admission_policy_sha256": trust["admission_policy_sha256"],
                "admission_sha256": admission["receipt_sha256"],
                "boot_id": final["boot_id"], "pid": final["pid"],
                "start_ticks": final["start_ticks"], "tgid": final["tgid"],
                "manager_pid": manager["instance"]["pid"],
                "manager_start_ticks": manager["instance"]["start_ticks"],
                "actual_argv": tuple(final["argv"]), "actual_cwd": final["cwd"],
                "actual_executable": final["exe"],
                "executable_sha256": executable_hash, "source_sha256": source_hashes,
                "fresh_read_monotonic_interval": (began, ended),
                "callback_sample_id": callback_sample_id,
                "live_observation": True,
                "ownership_granted": False, "simulation_permission": False,
            })
        except _NotCurrent as outcome:
            return MappingProxyType({
                "classification": outcome.classification,
                "role_name": role_name, "pid": candidate["pid"],
                "start_ticks": candidate["start_ticks"],
                "actual_launch_id": launch["actual_launch_id"] if launch else None,
                "callback_sample_id": callback_sample_id,
                "live_observation": False,
                "ownership_granted": False, "simulation_permission": False,
            })
        except ExternalCPUReject:
            raise
        except (OSError, KeyError, TypeError, ValueError) as error:
            raise ExternalCPUReject("EXTERNAL_CPU_VIEW_UNAVAILABLE_OR_MALFORMED") from error
