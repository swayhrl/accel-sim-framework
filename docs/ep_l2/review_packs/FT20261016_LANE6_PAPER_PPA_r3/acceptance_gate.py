#!/usr/bin/python3
"""Read-only, online scientific acceptance gate. No historical/offline plot bypass.

Execution terminal state and an immutable old qualification are insufficient.
The live Lane-5 ref is resolved at intake and again immediately before emission.
Git commit/digests bind the acceptance table, validation matrix, receipt and the
entire supersession evidence pack. Original run states are never rewritten.
"""
import hashlib
import json
from pathlib import PurePosixPath
import subprocess

AUTHORITY_URL = "git@github.com:swayhrl/accel-sim-framework.git"
AUTHORITY_REF = "refs/heads/hrl/ep-l2-ft20261016-lane5-v1"
AUTHORITY_FLOOR = "b134f76d8f4cd759c0852b68edf922ecbd445ea9"
REPORT = "docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/"
REVOKED_CORE = {"126394be46b15f55b9756d43eb9ca9a9baae1c84",
                "be651ccfe7bd47c0bbd8c30fe6439ae3b60cf8de"}
REVOKED_BINARY = {"0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698",
                  "2d2fb08217723bf920a486dcdce3412ca03c4a14028c9d67b401fd9b8a6d4664"}
IDENTITY_KEYS = ("core_source_commit", "framework_source_commit", "binary_sha256",
                 "runtime_config_sha256", "trace_content_sha256")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def path_ok(path):
    if not isinstance(path, str) or not path:
        return False
    p = PurePosixPath(path)
    return not p.is_absolute() and ".." not in p.parts


def remote_head():
    try:
        rows = subprocess.check_output(["git", "ls-remote", "--exit-code", AUTHORITY_URL, AUTHORITY_REF],
                                       timeout=30).decode().splitlines()
        require(len(rows) == 1, "Ambiguous live Lane-5 authority")
        commit, ref = rows[0].split()
        require(ref == AUTHORITY_REF and len(commit) == 40, "Invalid authority ref")
        return commit
    except (subprocess.SubprocessError, OSError) as e:
        raise ValueError("Cannot establish current Lane-5 authority; fail closed") from e


class AcceptanceSnapshot:
    """Loaded from Git by load_current_acceptance; not a normalized packet field."""
    def assert_fresh(self):
        require(remote_head() == self.commit, "Stale acceptance publication; fetch and bind latest Lane-5 revision")

    def check_run(self, run):
        key, identity = run["run_key"], run["identity"]
        records = [r for r in self.table["rows"] if r.get("run_key") == key]
        require(len(records) == 1, "Missing/duplicate scientific acceptance row")
        row = records[0]
        for name in IDENTITY_KEYS:
            require(row.get(name) == identity.get(name), "Scientific acceptance identity mismatch: " + name)
        for name in ("workload", "mode", "raw_log_sha256"):
            require(row.get(name) == run.get(name), "Scientific acceptance binding mismatch: " + name)
        require(row.get("original_terminal_status") == run["status"] == "COMPLETE_VALID",
                "Execution terminal mismatch; not a completed application")
        require(row.get("scientific_acceptance") == "CURRENT_ACCEPTED",
                "SCIENTIFIC_ACCEPTANCE_SUSPENDED_OR_UNACCEPTED: " + str(row.get("scientific_acceptance")))
        require(identity["core_source_commit"] not in REVOKED_CORE and identity["binary_sha256"] not in REVOKED_BINARY,
                "Revoked R0/R1 identity cannot be requalified; use new repaired source/binary/run-key")
        if "summary" in run:
            require(row.get("observed_cycles") == run["summary"].get("cycles")
                    and row.get("instructions") == run["summary"].get("instructions"),
                    "Accepted/native totals mismatch")
        require(self.table.get("status") == "CURRENT_ACCEPTED", "Application acceptance is not CURRENT_ACCEPTED")
        release = self.matrix.get(self.release_key, {})
        require(release.get("status") == "CURRENT_ACCEPTED", "Release validation matrix is not CURRENT_ACCEPTED")
        matching = [r for r in release.get("formal_runs", []) if r.get("run_key") == key]
        require(len(matching) == 1 and matching[0].get("scientific_acceptance") == "CURRENT_ACCEPTED"
                and matching[0].get("original_terminal_status") == "COMPLETE_VALID"
                and matching[0].get("workload") == run["workload"] and matching[0].get("mode") == run["mode"],
                "Acceptance/matrix supersession conflict")

    def provenance(self):
        return {"authority_url": AUTHORITY_URL, "authority_ref": AUTHORITY_REF,
                "publication_commit": self.commit, "release_key": self.release_key,
                "files": list(self.bindings), "freshness_policy": "LIVE_REF_AT_INTAKE_AND_BEFORE_EMISSION"}


def load_current_acceptance(repo, binding):
    require(isinstance(binding, dict), "Explicit current application acceptance binding required")
    commit = binding.get("publication_commit")
    require(isinstance(commit, str) and len(commit) == 40, "Exact acceptance publication required")
    require(commit == remote_head(), "Stale acceptance publication; fetch and bind latest Lane-5 revision")
    try:
        subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", AUTHORITY_FLOOR, commit],
                       check=True, capture_output=True, timeout=30)
    except subprocess.SubprocessError as e:
        raise ValueError("Acceptance predates mandatory R0/R1 revocation authority") from e
    obj = AcceptanceSnapshot()
    obj.commit, obj.release_key, obj.bindings = commit, binding.get("release_key"), []
    require(isinstance(obj.release_key, str) and bool(obj.release_key), "Explicit matrix release key required")

    def read(path, expected=None):
        require(path_ok(path), "Unsafe publication path")
        try:
            b = subprocess.check_output(["git", "-C", str(repo), "show", commit + ":" + path], timeout=30)
        except subprocess.SubprocessError as e:
            raise ValueError("Missing authoritative evidence: " + path) from e
        if expected is not None:
            require(sha(b) == expected, "Acceptance/supersession digest mismatch: " + path)
        obj.bindings.append({"path": path, "sha256": sha(b), "bytes": len(b)})
        return b

    loaded = {}
    for name in ("APPLICATION_ACCEPTANCE.json", "VALIDATION_MATRIX.json", "RECEIPT.json"):
        require(name in binding.get("sha256", {}), "Missing explicit acceptance digest: " + name)
        loaded[name] = json.loads(read(REPORT + name, binding["sha256"][name]))
    obj.table, obj.matrix = loaded["APPLICATION_ACCEPTANCE.json"], loaded["VALIDATION_MATRIX.json"]
    receipt = loaded["RECEIPT.json"]
    require(receipt.get("lane_id") == 5, "Acceptance must be published by Lane 5")
    names = [a if isinstance(a, str) else a.get("path", "") for a in receipt.get("artifacts", [])]
    require(REPORT + "APPLICATION_ACCEPTANCE.json" in names, "Receipt does not name acceptance table")
    base = obj.table.get("evidence_pack", "")
    require(path_ok(base) and base.startswith("docs/ep_l2/review_packs/"), "Missing supersession evidence pack")
    require(base in names, "Receipt does not name supersession pack")
    require("supersession_SHA256SUMS" in binding.get("sha256", {}), "Missing supersession checksum binding")
    sums = read(base + "/SHA256SUMS", binding["sha256"]["supersession_SHA256SUMS"]).decode().splitlines()
    require(bool(sums), "Empty supersession evidence closure")
    seen = set()
    for line in sums:
        digest, relative = line.split("  ", 1)
        require(path_ok(relative) and relative not in seen, "Invalid/duplicate supersession path")
        seen.add(relative)
        read(base + "/" + relative, digest)
    # The actual Lane-5 schema carries the release-level revocation in matrix;
    # the complete checksummed pack includes its preserved prior certificates.
    for release in obj.matrix.values():
        if isinstance(release, dict) and release.get("repair_manifest", "").startswith(base + "/"):
            require(release["repair_manifest"][len(base) + 1:] in seen, "Unclosed repair manifest")
    require(isinstance(obj.table.get("rows"), list), "Missing acceptance rows")
    keys = [r.get("run_key") for r in obj.table["rows"]]
    require(len(keys) == len(set(keys)) and all(keys), "Duplicate/empty acceptance keys")
    obj.assert_fresh()
    return obj
