#!/usr/bin/env python3
"""One-shot Lane5 dependency event read. No registry writer or resource waiter.

A candidate row is not a paper result. --adapter invokes the preserved native
intake and eleven evidence gates; no adapter means no numeric result is emitted.
"""
import argparse, datetime, hashlib, importlib.util, json, os
from pathlib import Path
import subprocess, sys

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.with_name("FT20261016_LANE6_PAPER_PPA_r4")
PIN = "20676888aa9f1d98bb318573a6569f5fe88aa17a"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--adapter", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.output.exists():
        raise ValueError("new immutable observation path required")
    source = PREVIOUS / "current_pair_intake.py"
    exact = subprocess.check_output(["git", "show", PIN + ":" + str(source.relative_to(repo))], cwd=repo)
    if exact != source.read_bytes():
        raise ValueError("previous consumer changed")
    spec = importlib.util.spec_from_file_location("pinned_current_intake", source)
    intake = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(intake)
    state = intake.fetch_state(repo)
    context = intake.bridge(repo, state)
    manifest = intake.vendor_api().current_manifest(state)
    candidates = []
    for row in manifest["rows"]:
        if row["scientific_acceptance"] != "CURRENT_ACCEPTED":
            continue
        # V2 release withdrawal and exact totals/log/identity checks precede
        # even candidate reporting. Native bytes still need --adapter below.
        intake.vendor_api().require_current_result(row["identity"], row["raw_log_sha256"], row["observed_cycles"], row["instructions"], state)
        candidates.append({k:row[k] for k in ["run_key", "workload", "mode", "identity", "raw_log_sha256"]})
    result = {
        "time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "authority": state["binding"],
        "consumer_commit": PIN,
        "consumer_sha256": hashlib.sha256(exact).hexdigest(),
        "status": "CURRENT_ROWS_REQUIRE_NATIVE_PAIR_ADAPTER" if candidates else "NO_CURRENT_ACCEPTED_PAIR",
        "accepted_row_candidates": candidates,
        "paper_results_emitted": False,
        "formal_performance_figures": [],
        "geomean": None,
        "new_registry_claims": 0,
        "background_waiter": None,
    }
    if args.adapter:
        result["native_intake"] = intake.consume(repo, json.loads(args.adapter.read_text()), state)
        result["paper_results_emitted"] = True
        result["status"] = "CURRENT_NATIVE_PAIR_VALIDATED_FOR_NEW_PAPER_REVISION"
    context.assert_fresh()
    with args.output.open("x") as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")
    print(json.dumps({"status": result["status"], "current_rows":len(candidates), "authority":result["authority"]}))

if __name__ == "__main__":
    main()
