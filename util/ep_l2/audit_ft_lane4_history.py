#!/usr/bin/env python3
"""Bounded, read-only EP-L2 ref/result audit. Never promotes an old row to B16."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

PATTERN = r"ceiling|ideal|perfect|unbounded|infinite|headroom|I_WB|I_META|I_READ_HIT"
ALLOWED = {".md", ".csv", ".json", ".config", ".cfg", ".py", ".cc", ".h", ".sh"}


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if r.returncode not in (0, 1):
        raise RuntimeError(r.stderr)
    return r.stdout


def digest(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()


def scan_refs(repo):
    refs = []
    tips = {}
    for line in git(repo, "for-each-ref", "--format=%(refname) %(objectname)",
                    "refs/heads", "refs/remotes").splitlines():
        ref, sha = line.split()
        if "/hrl/ep-l2-" not in ref or "ft20261016" in ref:
            continue
        refs.append({"ref": ref, "commit": sha})
        tips.setdefault(sha, []).append(ref)
    scans = []
    for sha, names in sorted(tips.items()):
        # Restrict grep to research text/code. Figures and raw logs are excluded.
        files = [f for f in git(repo, "ls-tree", "-r", "--name-only", sha).splitlines()
                 if (f.startswith(("docs/ep_l2/", "util/ep_l2/", "tests/ep_l2/",
                                   "src/gpgpu-sim/")) and Path(f).suffix in ALLOWED)]
        matches = []
        for start in range(0, len(files), 150):
            out = git(repo, "grep", "-I", "-i", "-n", "-E", PATTERN, sha,
                      "--", *files[start:start + 150]) if files[start:start + 150] else ""
            matches.extend(out.splitlines())
        scans.append({"commit": sha, "refs": names, "files_searched": len(files),
                      "matching_lines": matches})
    return {"repository": str(repo), "refs": refs, "tips": scans}


def scan_local(roots):
    found = []
    counts = {}
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            continue
        visited = 0
        for directory, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if d not in {".git", "build", "__pycache__",
                                                   "figures", "bin", "checkpoints"}]
            for name in names:
                p = Path(directory) / name
                if p.suffix not in {".md", ".json", ".csv", ".config", ".cfg"}:
                    continue
                if p.stat().st_size > 4 * 1024 * 1024:
                    continue
                visited += 1
                text = p.read_text(errors="replace")
                if re.search(PATTERN, text, re.I):
                    lines = [x[:1200] for x in text.splitlines() if re.search(PATTERN, x, re.I)]
                    found.append({"path": str(p), "sha256": digest(p), "matches": lines})
        counts[str(root)] = visited
    return {"metadata_files_searched": counts, "matches": found,
            "scope": "Only EP-L2 roots, metadata <=4MiB; raw logs not blindly scanned."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--framework", type=Path, required=True)
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    data = {"framework": scan_refs(a.framework), "core": scan_refs(a.core)}
    roots = []
    for name in ("results", "worktrees"):
        base = a.workspace / name
        if base.exists():
            for p in sorted(base.iterdir()):
                if name == "results" and p.name.startswith("ep_l2") and "ft20261016" not in p.name:
                    roots.append(p)
                elif name == "worktrees" and p.name.startswith("accel-sim-ep-l2") and "ft20261016" not in p.name:
                    for sub in ("docs/ep_l2", "tests/ep_l2"):
                        if (p / sub).is_dir(): roots.append(p / sub)
    data["local_results"] = scan_local(roots)
    (a.out / "HISTORY_SEARCH.json").write_text(json.dumps(data, indent=2) + "\n")
    # These are evidence classes, not fabricated performance rows. Exact source
    # identities and individual inputs are retained in the indexed artifacts.
    entries = [
        ("D256_D512_L1_CALIBRATION", "HISTORICAL_ONLY", "512 descriptors and L1 sensitivity", "WBUF absent; other L2 limits and lower path retained", "docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1/CALIBRATION_DELTAS_FINAL.csv"),
        ("LINE_MSHR_M256", "HISTORICAL_ONLY", "Line-MSHR 128 to 256", "descriptor/per-address/WAD/lower limits retained; not complete I_META", "docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/CONVOLUTION_2X2.csv"),
        ("WBUF_SHADOW_C4_C8_C16", "HISTORICAL_ONLY", "observational projections only", "no physical finite WBUF timing change; not I_WB", "docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/wbuf_sensitivity.csv"),
        ("H_SCHED_H_L2D_H_BW", "PLAN_ONLY", "specified downstream headroom axes", "plan is not a run", "docs/ep_l2/project_spec/PERFORMANCE_HEADROOM_PLAN.md"),
        ("OLD_L2_IDEAL_SWITCH", "HISTORICAL_ONLY", "registered legacy l2_ideal knob", "registration is not proof of a qualified runtime service or completed result", "src/gpgpu-sim/gpu-sim.cc"),
    ]
    fields = ["asset", "classification", "relaxed_resources", "retained_or_missing_constraints",
              "evidence_path", "new_B16_comparable", "binary_sha256", "config_sha256",
              "trace_identity", "terminal", "feature_vector", "ideal_vector",
              "core_source_commit", "framework_source_commit", "raw_log", "raw_log_sha256"]
    with (a.out / "REUSE_AUDIT.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for asset, classification, relaxed, constraints, path in entries:
            w.writerow(dict(asset=asset, classification=classification, relaxed_resources=relaxed,
                            retained_or_missing_constraints=constraints, evidence_path=path,
                            new_B16_comparable="NO", binary_sha256="NOT_ESTABLISHED_FOR_NEW_B16",
                            config_sha256="SEE_ORIGINAL_RUN_AUDIT", trace_identity="SEE_ORIGINAL_RUN_INDEX",
                            terminal="SEE_ORIGINAL_EVIDENCE", feature_vector="HISTORICAL",
                            ideal_vector="NOT_A_QUALIFIED_NEW_IDEAL"))
        for mode in ("I_WB", "I_META", "I_WB_META", "I_READ_HIT"):
            w.writerow(dict(asset=mode + "_B16", classification="ABSENT",
                            relaxed_resources="NOT_RUN", retained_or_missing_constraints="No source/config/binary/trace matched B16 result found at audit",
                            new_B16_comparable="NOT_RUN", terminal="NOT_RUN"))
        # Preserve each retained runtime identity. Missing provenance remains
        # explicit, rather than promoting same-name workloads or guessed OFF bits.
        status_paths = sorted({p for root in roots for p in Path(root).rglob('run_status.json')
                               if p.is_file()})
        for p in status_paths:
            r = json.loads(p.read_text())
            a1 = r.get('audit', {})
            a2 = r.get('source', {})
            def value(*keys):
                for obj in (r, a1, a2):
                    for key in keys:
                        if obj.get(key) is not None: return obj[key]
                return 'NOT_RETAINED'
            terminal = value('status')
            klass = 'HISTORICAL_ONLY' if terminal == 'COMPLETE_VALID' else 'PARTIAL'
            w.writerow(dict(asset=str(p), classification=klass,
                            relaxed_resources='SEE_ORIGINAL_CONFIG',
                            retained_or_missing_constraints='Historical model; no B16 finite-WBUF matching source/binary/config',
                            evidence_path=str(p), new_B16_comparable='NO',
                            core_source_commit=value('core_sha', 'core_commit', 'core_authoritative_source'),
                            framework_source_commit=value('framework_sha', 'framework_commit', 'framework_authoritative_source'),
                            binary_sha256=value('binary_sha256', 'simulator_sha256', 'executable_sha256'),
                            config_sha256=value('runtime_config_composite_sha256', 'config_sha256'),
                            trace_identity=value('trace', 'trace_id'), terminal=terminal,
                            feature_vector=json.dumps(value('ep_l2_features', 'feature_vector'), sort_keys=True),
                            ideal_vector=json.dumps(value('ideal_vector'), sort_keys=True),
                            raw_log=value('raw_log_gz', 'raw_log'),
                            raw_log_sha256=value('raw_log_gz_sha256', 'raw_log_sha256')))
    print(json.dumps({"framework_refs": len(data['framework']['refs']),
                      "core_refs": len(data['core']['refs']),
                      "local_metadata_files": sum(data['local_results']['metadata_files_searched'].values()),
                      "out": str(a.out)}))


if __name__ == "__main__":
    main()
