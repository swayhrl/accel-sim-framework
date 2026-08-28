#!/usr/bin/env python3
import csv
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SAMPLE = pathlib.Path(__file__).with_name("sample_l2charv1.log")

with tempfile.TemporaryDirectory() as temporary:
    output = pathlib.Path(temporary)
    subprocess.check_call(["python3", str(ROOT / "parse_l2_char.py"), str(SAMPLE), "--out", str(output)])
    assert list(csv.DictReader((output / "slice.csv").open()))[0]["slice"] == "0"
    assert list(csv.DictReader((output / "window.csv").open()))[0]["window"] == "0"
    assert json.load((output / "manifest.json").open())["schema_version"] == "L2CHARV1"

    # Per-kernel simulator statistics may precede the terminal snapshot.
    # Repeating a valid snapshot must not duplicate final CSV windows.
    doubled = output / "two_snapshots.log"
    doubled.write_text(SAMPLE.read_text() + SAMPLE.read_text())
    final_only = output / "final_only"
    subprocess.check_call(["python3", str(ROOT / "parse_l2_char.py"), str(doubled), "--out", str(final_only)])
    assert len(list(csv.DictReader((final_only / "slice.csv").open()))) == 1
    assert len(list(csv.DictReader((final_only / "window.csv").open()))) == 1

    rejected = subprocess.run(["python3", str(ROOT / "parse_l2_char.py"), str(SAMPLE),
                               "--out", str(output / "production"), "--production"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert rejected.returncode != 0

    multi = output / "two_slices.log"
    multi.write_text("\n".join([
        "gpu_tot_sim_cycle = 9", "gpu_tot_sim_cycle = 12",
        "gpu_tot_sim_insn = 90", "gpu_tot_sim_insn = 120",
        "L2CHARV1|SLICE|slice=0|cycles=4|mshr_avg=0.5|missq_avg=0|draml2q_avg=0|l2dramq_avg=0",
        "L2CHARV1|SLICE|slice=1|cycles=4|mshr_avg=1.75|missq_avg=0|draml2q_avg=0|l2dramq_avg=0",
        "L2CHARV1|HIST|slice=0|metric=mshr|capacity=8|unbounded=0|samples=4|bins=2,2,0,0,0,0,0,0,0",
        "L2CHARV1|HIST|slice=1|metric=mshr|capacity=8|unbounded=0|samples=4|bins=0,1,3,0,0,0,0,0,0",
    ]))
    merged = output / "merged"
    subprocess.check_call(["python3", str(ROOT / "parse_l2_char.py"), str(multi), "--out", str(merged)])
    row = list(csv.DictReader((merged / "summary.csv").open()))[0]
    assert row["mshr_global_max"] == "2"
    assert row["mshr_global_p50"] == "1"
    assert row["mshr_global_p95"] == "2"
    assert float(row["mshr_global_avg"]) == 1.125
    assert row["gpu_tot_sim_cycle"] == "12" and row["gpu_tot_sim_insn"] == "120"
