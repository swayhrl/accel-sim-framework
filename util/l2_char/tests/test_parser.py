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
