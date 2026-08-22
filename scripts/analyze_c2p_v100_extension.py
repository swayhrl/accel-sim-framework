#!/usr/bin/env python3
"""Audit the V100 ISPASS/Pannotia C2P extension without mixing paper16 data."""

import argparse
import csv
import hashlib
from pathlib import Path


MODES = ("baseline", "oracle", "ideal", "c2p", "ata", "ccd", "ring")
MODE_CONTRACT = {
    "baseline": {"-c2p_cache_enable": "0", "-c2p_cache_oracle_only": "0"},
    "oracle": {"-c2p_cache_enable": "0", "-c2p_cache_oracle_only": "1"},
    "ideal": {"-c2p_cache_enable": "1", "-c2p_cache_ideal_peer": "1"},
    "c2p": {"-c2p_cache_enable": "1", "-c2p_cache_scheme": "0"},
    "ata": {"-c2p_cache_enable": "1", "-c2p_cache_scheme": "1"},
    "ccd": {"-c2p_cache_enable": "1", "-c2p_cache_scheme": "2"},
    "ring": {"-c2p_cache_enable": "1", "-c2p_cache_scheme": "3"},
}


def manifest_rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader((line for line in stream
                                    if not line.startswith("#")),
                                   delimiter="\t"))


def options(path):
    if not path.is_file():
        return {}
    value = {}
    for line in path.read_text(errors="replace").splitlines():
        fields = line.split("#", 1)[0].split()
        if len(fields) >= 2 and fields[0].startswith("-"):
            value[fields[0]] = fields[1]
    return value


def summary(path):
    if not path.is_file():
        return None
    value = {}
    for line in path.read_text(errors="replace").splitlines():
        if " = " not in line:
            continue
        key, raw = line.split(" = ", 1)
        try:
            value[key] = int(raw)
        except ValueError:
            pass
    return value


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_run(root, case, mode, expected_l2):
    run = root / case / mode
    data = summary(run / "summary.txt")
    out = run / "run.out"
    if data is None:
        return {"status": "missing", "reason": "summary absent", "data": {}}
    if not out.is_file() or "GPGPU-Sim: *** exit detected ***" not in out.read_text(errors="replace"):
        return {"status": "fail", "reason": "normal exit marker absent", "data": data}
    got = options(run / "gpgpusim.config")
    errors = []
    for key, expected in MODE_CONTRACT[mode].items():
        if got.get(key) != expected:
            errors.append(f"{key}={got.get(key, '<absent>')} expected {expected}")
    if got.get("-gpgpu_l2_rop_latency") != str(expected_l2):
        errors.append("L2 ROP latency mismatch")
    remote = data.get("c2p_remote_hits", 0)
    avoided = data.get("c2p_l2_requests_avoided", 0)
    if mode not in ("baseline", "oracle") and remote != avoided:
        errors.append("remote_hits != l2_requests_avoided")
    if mode == "ring" and data.get("c2p_queries_queue_bypass", 0) != 0:
        errors.append("ring query queue bypass is nonzero")
    return {"status": "pass" if not errors else "fail",
            "reason": "; ".join(errors), "data": data}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--main-root", type=Path, required=True)
    parser.add_argument("--l2-50-root", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []
    provenance = []
    for item in manifest_rows(args.manifest):
        archive = args.archive_root / item["archive"]
        archive_ok = archive.is_file() and sha256(archive) == item["archive_sha256"]
        if not archive_ok:
            failures.append(f"{item['case']}: archive hash mismatch or absent")
        checks = {}
        for mode in MODES:
            main_run = inspect_run(args.main_root, item["case"], mode, 200)
            fast_run = inspect_run(args.l2_50_root, item["case"], mode, 50)
            checks[mode] = (main_run, fast_run)
            for label, run in (("main", main_run), ("l2_50", fast_run)):
                if run["status"] != "pass":
                    failures.append(f"{item['case']}/{mode}/{label}: {run['status']} {run['reason']}")
                data = run["data"]
                rows.append({
                    "case": item["case"], "suite": item["suite"], "mode": mode,
                    "archive_sha256_ok": archive_ok, "root": label,
                    "status": run["status"], "reason": run["reason"],
                    "cycles": data.get("gpu_tot_sim_cycle", ""),
                    "instructions": data.get("gpu_sim_insn", ""),
                    "l2_accesses": data.get("l2_total_cache_accesses", ""),
                    "remote_hits": data.get("c2p_remote_hits", ""),
                    "l2_avoided": data.get("c2p_l2_requests_avoided", ""),
                })
        baseline_main = checks["baseline"][0]["data"]
        oracle_main = checks["oracle"][0]["data"]
        if baseline_main and oracle_main and baseline_main.get("gpu_tot_sim_cycle") != oracle_main.get("gpu_tot_sim_cycle"):
            failures.append(f"{item['case']}: main oracle cycles differ from baseline")
        provenance.append({
            "case": item["case"],
            "suite": item["suite"],
            "command/input": item["command/input"],
            "input_sha256": item["input_sha256"],
            "archive": item["archive"],
            "archive_sha256_ok": archive_ok,
            "main_passed": sum(run[0]["status"] == "pass" for run in checks.values()),
            "l2_50_passed": sum(run[1]["status"] == "pass" for run in checks.values()),
        })

    columns = tuple(rows[0]) if rows else ()
    with (args.out_dir / "extension_modes.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader(); writer.writerows(rows)
    with (args.out_dir / "extension_provenance.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(provenance[0]))
        writer.writeheader(); writer.writerows(provenance)
    total = len(rows)
    passed = sum(row["status"] == "pass" for row in rows)
    report = ["# V100 C2P extension audit", "",
              f"- Mode roots checked: {total}; passed: {passed}; incomplete/failed: {total - passed}.",
              "- This report is deliberately separate from the canonical paper16 aggregate.",
              "- Archive hashes, mode contracts, L2 latency, exit markers, remote-hit conservation, and Ring backpressure are checked.",
              ""]
    report += ["## Trace provenance and progress", "",
               "| case | suite | input | input SHA-256 | archive SHA valid | main | L2=50 |",
               "|---|---|---|---|---:|---:|---:|"]
    for item in provenance:
        report.append(
            "| {case} | {suite} | `{command/input}` | `{input_sha256}` | {archive_sha256_ok} | "
            "{main_passed}/7 | {l2_50_passed}/7 |".format(**item))
    report += ["", "`extension_provenance.csv` carries the same provenance and progress in machine-readable form.", ""]
    if failures:
        report += ["## Pending or failed checks", ""] + [f"- {item}" for item in failures]
    else:
        report += ["## Result", "", "All extension roots pass the strict audit."]
    (args.out_dir / "extension_status.md").write_text("\n".join(report) + "\n")
    if args.strict and failures:
        raise SystemExit("strict V100 extension audit failed; see extension_status.md")


if __name__ == "__main__":
    main()
