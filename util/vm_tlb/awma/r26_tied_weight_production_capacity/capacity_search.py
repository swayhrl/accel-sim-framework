#!/usr/bin/env python3
"""Deterministic fresh-process natural-OOM search for AWMA R26."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path


EXP = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)
POLICIES = ("c1", "s2")


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


class Search:
    def __init__(self, a):
        if os.environ.get("R26_GPU_LOCK_HELD") != "1":
            raise RuntimeError("capacity parent requires shared-lock sentinel")
        self.a = a
        self.root = Path(a.root)
        self.outdir = self.root / "raw/capacity_trials"
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.logs = self.root / "logs/capacity_trials"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.rows = []
        self.serial = 0

    def trial(self, policy, batch, kind, rep=0):
        self.serial += 1
        stem = f"{self.serial:03d}_{kind}_{policy}_B{batch}_R{rep}"
        receipt = self.outdir / f"{stem}.json"
        log = self.logs / f"{stem}.log"
        cmd = [
            self.a.python, self.a.runner, "--mode", "probe", "--root", self.a.root,
            "--model", self.a.model, "--tokens", self.a.tokens, "--common", self.a.common,
            "--policy", policy, "--batch", str(batch), "--output", str(receipt),
        ]
        started = time.time()
        try:
            with log.open("w") as f:
                proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=300)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            exit_code = 124
            value = {"outcome": "UNKNOWN", "status": "TIMEOUT", "policy": policy, "batch": batch, "timeout_seconds": 300}
            write_json(receipt, value)
        if not receipt.exists():
            value = {"outcome": "UNKNOWN", "status": "MISSING_RECEIPT", "policy": policy, "batch": batch, "exit_code": exit_code}
            write_json(receipt, value)
        value = json.loads(receipt.read_text())
        outcome = value.get("outcome", "UNKNOWN")
        row = {
            "serial": self.serial, "kind": kind, "rep": rep, "policy": policy, "batch": batch,
            "outcome": outcome, "exit_code": exit_code, "receipt": str(receipt),
            "receipt_bytes": receipt.stat().st_size, "log": str(log),
            "elapsed_seconds": time.time() - started,
            "oom_phase": value.get("oom_phase", ""),
        }
        self.rows.append(row)
        print(json.dumps({"capacity_trial": row}, sort_keys=True), flush=True)
        if outcome not in ("PASS", "OOM"):
            raise RuntimeError(f"capacity trial unknown: {row}")
        return outcome

    def search_policy(self, policy):
        attempted = {}
        low = None; high = None; censored = False
        for batch in EXP:
            outcome = self.trial(policy, batch, "search")
            attempted[batch] = outcome
            if outcome == "PASS":
                low = batch
                if batch == 512:
                    censored = True
                    break
            else:
                high = batch
                break
        if low is None:
            raise RuntimeError(f"{policy} B1 did not pass")
        while not censored and high - low > 1:
            if len(attempted) >= 19:
                raise RuntimeError(f"{policy} search trial ceiling exceeded")
            mid = (low + high) // 2
            outcome = self.trial(policy, mid, "search")
            attempted[mid] = outcome
            if outcome == "PASS": low = mid
            else: high = mid
        ordered = sorted(attempted.items())
        seen_oom = False
        monotone = True
        for _, outcome in ordered:
            if outcome == "OOM": seen_oom = True
            elif seen_oom and outcome == "PASS": monotone = False
        return {"policy": policy, "largest_search_pass": low, "first_adjacent_oom": None if censored else high, "right_censored": censored, "attempted": attempted, "monotone": monotone}

    def confirm_one(self, policy, batch, expected, kind):
        outcomes = [self.trial(policy, batch, kind, rep) for rep in range(3)]
        return {"policy": policy, "batch": batch, "expected": expected, "outcomes": outcomes, "qualified": outcomes == [expected] * 3}

    def confirm_alternating(self, batch, expected_by_policy, kind):
        values = {p: [] for p in POLICIES}
        for rep in range(3):
            order = POLICIES if rep % 2 == 0 else tuple(reversed(POLICIES))
            for policy in order:
                values[policy].append(self.trial(policy, batch, kind, rep))
        return [{"policy": p, "batch": batch, "expected": expected_by_policy[p], "outcomes": values[p], "qualified": values[p] == [expected_by_policy[p]] * 3} for p in POLICIES]

    def run(self):
        searches = {p: self.search_policy(p) for p in POLICIES}
        confirmations = []
        c1, s2 = searches["c1"], searches["s2"]
        if not c1["monotone"] or not s2["monotone"]:
            summary = {
                "decision": "R26_CAPACITY_BOUNDARY_UNSTABLE", "searches": searches,
                "confirmations": [], "all_trials": self.rows, "unstable": True,
                "reason": "observed non-monotonic search outcomes",
            }
            write_json(self.root / "raw/CAPACITY_SEARCH_SUMMARY.json", summary)
            print(json.dumps(summary, indent=2, sort_keys=True)); return
        # Confirm passing endpoints, alternating when they coincide.
        if c1["largest_search_pass"] == s2["largest_search_pass"]:
            confirmations += self.confirm_alternating(c1["largest_search_pass"], {"c1": "PASS", "s2": "PASS"}, "confirm_pass_endpoint")
        else:
            confirmations.append(self.confirm_one("c1", c1["largest_search_pass"], "PASS", "confirm_pass_endpoint"))
            confirmations.append(self.confirm_one("s2", s2["largest_search_pass"], "PASS", "confirm_pass_endpoint"))
        # Confirm OOM endpoints, alternating when identical.
        if not c1["right_censored"] and not s2["right_censored"] and c1["first_adjacent_oom"] == s2["first_adjacent_oom"]:
            confirmations += self.confirm_alternating(c1["first_adjacent_oom"], {"c1": "OOM", "s2": "OOM"}, "confirm_oom_endpoint")
        else:
            if not c1["right_censored"]:
                confirmations.append(self.confirm_one("c1", c1["first_adjacent_oom"], "OOM", "confirm_oom_endpoint"))
            if not s2["right_censored"]:
                confirmations.append(self.confirm_one("s2", s2["first_adjacent_oom"], "OOM", "confirm_oom_endpoint"))
        unstable = not c1["monotone"] or not s2["monotone"] or not all(x["qualified"] for x in confirmations)
        confirmed = {p: searches[p]["largest_search_pass"] for p in POLICIES}
        b_common = min(confirmed.values())
        if unstable:
            summary = {
                "decision": "R26_CAPACITY_BOUNDARY_UNSTABLE", "searches": searches,
                "confirmations": confirmations, "all_trials": self.rows,
                "b_common": b_common, "unstable": True,
                "reason": "endpoint confirmation disagreement",
            }
            write_json(self.root / "raw/CAPACITY_SEARCH_SUMMARY.json", summary)
            print(json.dumps(summary, indent=2, sort_keys=True)); return
        witness = None; reverse = False
        if not c1["right_censored"] and c1["first_adjacent_oom"] == c1["largest_search_pass"] + 1 and s2["largest_search_pass"] > c1["largest_search_pass"]:
            witness = c1["first_adjacent_oom"]
        elif not s2["right_censored"] and s2["first_adjacent_oom"] == s2["largest_search_pass"] + 1 and c1["largest_search_pass"] > s2["largest_search_pass"]:
            witness = s2["first_adjacent_oom"]; reverse = True

        def covered(policy, batch, expected):
            return any(x["policy"] == policy and x["batch"] == batch and x["expected"] == expected and x["qualified"] for x in confirmations)

        common_conf = []
        for policy in POLICIES:
            if covered(policy, b_common, "PASS"):
                common_conf.append({"policy": policy, "batch": b_common, "expected": "PASS", "reused": True, "qualified": True})
            else:
                item = self.confirm_one(policy, b_common, "PASS", "confirm_common")
                confirmations.append(item); common_conf.append(item)
        witness_conf = []
        if witness is not None:
            expected = {"c1": "PASS" if reverse else "OOM", "s2": "OOM" if reverse else "PASS"}
            for policy in POLICIES:
                if covered(policy, witness, expected[policy]):
                    witness_conf.append({"policy": policy, "batch": witness, "expected": expected[policy], "reused": True, "qualified": True})
                else:
                    item = self.confirm_one(policy, witness, expected[policy], "confirm_witness")
                    confirmations.append(item); witness_conf.append(item)
        unstable |= not all(x["qualified"] for x in common_conf + witness_conf)
        if unstable:
            decision = "R26_CAPACITY_BOUNDARY_UNSTABLE"
        elif witness is not None and not reverse:
            decision = "R26_INTEGRATED_BATCH_CAPACITY_EXTENSION_SUPPORTED"
        elif witness is not None and reverse:
            decision = "R26_S2_BATCH_CAPACITY_REGRESSION"
        elif c1["right_censored"] or s2["right_censored"]:
            decision = "R26_CAPACITY_SEARCH_RIGHT_CENSORED"
        elif c1["largest_search_pass"] == s2["largest_search_pass"]:
            decision = "R26_NO_BATCH_CAPACITY_EXTENSION"
        else:
            raise RuntimeError("unhandled capacity decision state")
        summary = {
            "decision": decision, "searches": searches, "confirmations": confirmations,
            "b_common": b_common, "witness": witness, "reverse_witness": reverse,
            "witness_confirmations": witness_conf, "common_confirmations": common_conf,
            "all_trials": self.rows, "max_batch": 512, "only_variable": "physical batch",
            "natural_oom_only": True, "unstable": unstable,
        }
        write_json(self.root / "raw/CAPACITY_SEARCH_SUMMARY.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True))


def main():
    p = argparse.ArgumentParser()
    for name in ("root", "python", "runner", "model", "tokens", "common"):
        p.add_argument(f"--{name}", required=True)
    Search(p.parse_args()).run()


if __name__ == "__main__":
    main()
