#!/usr/bin/env python3
"""EPL2SRV1 parser regression and fail-close checks."""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
PARSER = ROOT / "util/ep_l2/parse_epl2_sector_reuse.py"
FIELDS = ("total_sector_reference_events=2|excluded_writeback_requests=0|"
          "new_sector_on_new_line_events=1|new_sector_on_seen_line_events=0|"
          "temporal_sector_reuse_instances=1|unique_sector_identities=1|"
          "unique_sectors_reused_at_least_once=1|one_touch_unique_sectors=0|"
          "sector_reuse_le8=1|sector_reuse_9_16=0|sector_reuse_17_32=0|"
          "sector_reuse_33_64=0|sector_reuse_65_128=0|sector_reuse_129_256=0|"
          "sector_reuse_257_512=0|sector_reuse_513_1024=0|"
          "sector_reuse_1025_2048=0|sector_reuse_2049_4096=0|sector_reuse_gt4096=0")
base = "EPL2SRV1|scope=application|slice={slice}|kernel_uid=18446744073709551615|" + FIELDS + "\n"
args = ("--workload", "fixture", "--framework-commit", "f", "--core-commit", "c",
        "--config-sha256", "d", "--trace-id", "t")
with tempfile.TemporaryDirectory() as temp:
    temp = pathlib.Path(temp); log = temp / "fixture.log"
    log.write_text("".join(base.format(slice=item) for item in range(2)))
    run = subprocess.run((sys.executable, str(PARSER), str(log), "--out", str(temp / "out"), *args, "--expected-slices", "2"), capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    summary = (temp / "out/sector_reuse_summary.csv").read_text()
    assert "sector_temporal_reuse_fraction" in summary and "0.5" in summary
    assert json.loads((temp / "out/manifest.json").read_text())["schema_version"] == "EPL2SRV1"
    log.write_text("".join(base.format(slice=item) for item in range(2)) + base.format(slice=0))
    run = subprocess.run((sys.executable, str(PARSER), str(log), "--out", str(temp / "dup"), *args, "--expected-slices", "2"), capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads((temp / "dup/manifest.json").read_text())["application_snapshot_records_superseded"] == 1
    advanced = (base.format(slice=0).replace("total_sector_reference_events=2", "total_sector_reference_events=3")
                .replace("temporal_sector_reuse_instances=1", "temporal_sector_reuse_instances=2")
                .replace("sector_reuse_le8=1", "sector_reuse_le8=2"))
    log.write_text("".join(base.format(slice=item) for item in range(2)) + advanced)
    run = subprocess.run((sys.executable, str(PARSER), str(log), "--out", str(temp / "advanced"), *args, "--expected-slices", "2"), capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    log.write_text("".join(base.format(slice=item) for item in range(2)) + base.format(slice=0).replace("temporal_sector_reuse_instances=1", "temporal_sector_reuse_instances=0").replace("sector_reuse_le8=1", "sector_reuse_le8=0").replace("one_touch_unique_sectors=0", "one_touch_unique_sectors=1"))
    run = subprocess.run((sys.executable, str(PARSER), str(log), "--out", str(temp / "bad"), *args, "--expected-slices", "2"), capture_output=True, text=True)
    assert run.returncode != 0 and "non-monotonic" in run.stderr
source = PARSER.read_text()
assert ".read_text(" not in source and ".read_bytes(" not in source
print("EPL2SRV1 parser regression: PASS")
