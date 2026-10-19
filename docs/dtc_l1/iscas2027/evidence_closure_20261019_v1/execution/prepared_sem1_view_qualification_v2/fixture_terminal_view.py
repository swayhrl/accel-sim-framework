"""PREPARED_NOT_TESTED. Readonly own-terminal projection for CPU fixture review.

No launch, signal, wait, adoption, resource sample or file read at import.
A terminal projection is authority-only: return the entire original all-project
snapshot, and never hide any foreign process/resource/lock. Only one same-child
Z race is handled; /proc absence and generic authority failures remain STOP.
"""
from copy import deepcopy
import os
from pathlib import Path
from subprocess import Popen

INSTANCE = ("boot_id", "pid", "start_ticks", "tgid")
ROLE = "SEM1_ACTUAL_OBJECT_FIXTURE_RUNTIME_V1"
RACE = "CPU_ROLE_INSTANCE_CHANGED_DURING_READ"


class OwnRootIdentityUnresolved(RuntimeError):
    pass


class _OwnRootTerminal(Exception):
    def __init__(self, proof):
        super().__init__("OWN_RETAINED_UNREAPED_PIDFD_ROOT_IS_Z")
        self.proof = proof


def eligible_terminal(record, current):
    """Pure boundary predicate; callers must independently establish fd/handle."""
    return bool(record and current and record.get("retained_direct_Popen") is True
        and record.get("unreaped") is True and record.get("pidfd_matches") is True
        and all(record["instance"].get(k) == current.get(k) for k in INSTANCE)
        and current.get("state") == "Z")


class FixtureTerminalView:
    def __init__(self, roles, *, current_launch, owner, identity_reader):
        # These public frozen functions remain unmodified. The caller hashes
        # the complete copied source closure before constructing this adapter.
        from cpu_admission_v2 import NoOwnedChildren
        from shared_authority import (SharedOwnership, fresh_process,
                                      review_with_exact_roles)
        from legacy_authority_runtime import (bind_frozen_procedures, DATA,
                                             exact_legacy_output_sources)
        import shared_authority
        import json
        _, self._snapshot, self._legacy_review = bind_frozen_procedures()
        self._roles = json.loads((Path(shared_authority.__file__).parent /
                                  "EXACT_EXTERNAL_ROLE_CONTRACTS.json").read_text())["roles"]
        self._roles += deepcopy(roles)
        self._shared = SharedOwnership(NoOwnedChildren(), identity_reader)
        self._frozen_review = review_with_exact_roles
        self._strict_image = fresh_process
        self._legacy_pack = DATA
        self._legacy_sources = exact_legacy_output_sources()
        self._launch = current_launch
        self._owner = deepcopy(owner)
        self._identity = identity_reader

    def _retained(self):
        launch = self._launch()
        if launch is None:
            return None
        proc, fd = launch.get("proc"), launch.get("pidfd")
        instance = launch.get("instance")
        if (not isinstance(proc, Popen) or proc.returncode is not None or
                not isinstance(instance, dict) or fd is None):
            raise OwnRootIdentityUnresolved("OWN_ROOT_HAS_NO_CURRENT_RETAINED_HANDLE")
        if instance.get("pid") != proc.pid:
            raise OwnRootIdentityUnresolved("OWN_HANDLE_AND_INSTANCE_PID_DISAGREE")
        try:
            name = os.readlink("/proc/self/fd/" + str(fd))
            entries = dict(line.split(":", 1) for line in
                           Path("/proc/self/fdinfo", str(fd)).read_text().splitlines()
                           if ":" in line)
            matching_fd = name == "anon_inode:[pidfd]" and int(entries["Pid"]) == proc.pid
            current = self._identity(proc.pid)
        except (OSError, KeyError, ValueError) as error:
            raise OwnRootIdentityUnresolved("OWN_UNREAPED_ROOT_ABSENT_OR_PIDFD_UNRESOLVED") from error
        if (not matching_fd or not all(instance.get(k) == current.get(k) for k in INSTANCE)
                or current.get("ppid") != self._owner["pid"]):
            raise OwnRootIdentityUnresolved("OWN_RETAINED_INSTANCE_OR_PIDFD_CHANGED")
        return {"retained_direct_Popen": True, "unreaped": True,
                "pidfd_matches": matching_fd, "instance": deepcopy(instance),
                "current": current, "role": launch["role"]["name"]}

    def _terminal_proof(self, pid):
        record = self._retained()
        if (record and record["role"] == ROLE and record["instance"]["pid"] == pid
                and eligible_terminal(record, record["current"])):
            return record
        return None

    def _reader(self, pid):
        try:
            return self._strict_image(pid, self._identity)
        except Exception as error:
            # Precise exception + exact owned target. No catch of an arbitrary
            # AuthorityReject in the outer review; all foreign errors propagate.
            launch = self._launch()
            same_target = (launch is not None and isinstance(launch.get("proc"), Popen)
                           and pid == launch["proc"].pid)
            allowed_error = isinstance(error, (FileNotFoundError, ProcessLookupError)) or str(error) == RACE
            if same_target and allowed_error:
                proof = self._terminal_proof(pid)
                if proof is not None:
                    raise _OwnRootTerminal(proof) from error
            raise

    def _review(self, classification):
        self._shared.update_peers([])
        return self._frozen_review(
            classification, self._legacy_review, self._owner, self._shared,
            self._roles, self._identity, self._legacy_pack, self._legacy_sources,
            process_reader=self._reader, require_external_launch_binding=True)

    def review(self, own_owner):
        # CPUAdmission passes vendor identity(), which has no boot_id field.
        # Verify its actual API fields, then independently read our boot-bound
        # current manager identity rather than inventing a field in that input.
        if (any(own_owner.get(k) != self._owner.get(k)
                for k in ("pid", "start_ticks", "tgid")) or
                own_owner.get("boot_id", self._owner["boot_id"]) != self._owner["boot_id"]):
            raise OwnRootIdentityUnresolved("REVIEW_OWNER_CHANGED")
        fresh_owner = self._identity(self._owner["pid"])
        if any(fresh_owner.get(k) != self._owner.get(k) for k in INSTANCE):
            raise OwnRootIdentityUnresolved("CURRENT_MANAGER_INSTANCE_CHANGED")
        # An absent unreaped own root is not silently accepted as a Z race.
        self._retained()
        full = self._snapshot()
        projected = []
        try:
            verdict = self._review(full)
        except _OwnRootTerminal as terminal:
            proof = self._terminal_proof(terminal.proof["instance"]["pid"])
            if proof is None:
                raise OwnRootIdentityUnresolved("OWN_TERMINAL_PROOF_NO_LONGER_CURRENT")
            key = tuple(proof["instance"][k] for k in ("pid", "start_ticks"))
            matching = [p for p in full["processes"]
                        if (p["pid"], p["start_ticks"]) == key]
            if len(matching) != 1:
                raise OwnRootIdentityUnresolved("OWN_TERMINAL_ROW_NOT_UNIQUE_IN_SNAPSHOT")
            classification = dict(full, processes=[
                p for p in full["processes"]
                if (p["pid"], p["start_ticks"]) != key])
            # One bounded metadata classification replay. Same complete snapshot
            # is returned below; every foreign row/lock is reviewed again.
            verdict = self._review(classification)
            projected = [{"instance": proof["instance"],
                          "fresh_terminal_identity": proof["current"],
                          "reason": "SAME_UNREAPED_PIDFD_OWN_ROOT_Z_NO_LIVE_IMAGE",
                          "live_observation": "UNAVAILABLE_NO_RETRY"}]
        for row in verdict.get("exact_external_CPU_controls", []):
            if row.get("role") != ROLE:
                continue
            record = self._retained()
            if (record is None or row["pid"] != record["instance"]["pid"] or
                    row["start_ticks"] != record["instance"]["start_ticks"]):
                raise OwnRootIdentityUnresolved("FOREIGN_MATCHING_FIXTURE_ROLE_NO_ADOPTION")
        verdict = dict(verdict,
            own_fixture_terminal_projection=projected,
            all_project_resource_population_unchanged=True,
            original_process_count=len(full["processes"]),
            authority_only_own_terminal_projection_count=len(projected))
        return full, verdict
