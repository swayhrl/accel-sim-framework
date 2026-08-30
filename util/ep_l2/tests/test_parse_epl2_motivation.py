#!/usr/bin/env python3
"""EPL2MOTV1 aggregation/accounting regression."""
import pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[3]
PARSER = ROOT / "util/ep_l2/parse_epl2_motivation.py"
base = "EPL2MOTV1|scope=application|slice={slice}|kernel_uid=18446744073709551615|eligible_demand_references=2|excluded_writeback_references=0|reuse_instances=1|reuse_le8=1|reuse_9_16=0|reuse_17_32=0|reuse_33_64=0|reuse_65_128=0|reuse_129_256=0|reuse_257_512=0|reuse_513_1024=0|reuse_gt1024=0|unique_lines=1|unique_lines_reused=1|one_touch_unique_lines=0|post_evictions=1|post_eviction_rerefs=1|post_eviction_seq_sum=1|post_eviction_cycle_sum=3|wb_packets_created=1|wb_packets_lower_accepted=1|wb_lifetime_sum=2|wb_lifetime_max=2|eligible_miss_cycles_4=1|blocked_miss_cycles_4=1|set_assoc_4=1|mshr_meta_4=0|missq_lower_4=0|wb_path_4=0|other_4=0|wbuf_opportunities_4=0|wbuf_would_block_4=0|eligible_miss_cycles_8=1|blocked_miss_cycles_8=1|set_assoc_8=1|mshr_meta_8=0|missq_lower_8=0|wb_path_8=0|other_8=0|wbuf_opportunities_8=0|wbuf_would_block_8=0|eligible_miss_cycles_16=1|blocked_miss_cycles_16=1|set_assoc_16=1|mshr_meta_16=0|missq_lower_16=0|wb_path_16=0|other_16=0|wbuf_opportunities_16=0|wbuf_would_block_16=0\n"
with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d); log = d / "x.log"; log.write_text("".join(base.format(slice=i) for i in range(64)))
    r = subprocess.run((sys.executable, str(PARSER), str(log), "--out", str(d / "out"), "--workload", "fixture", "--framework-commit", "f", "--core-commit", "c"), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "<=8" in (d / "out/reuse_distance.csv").read_text()
    # Application accounting is fail-closed: a partial/repeated terminal
    # record cannot be silently folded into a multi-GB streaming aggregation.
    log.write_text("".join(base.format(slice=i) for i in range(64)) + base.format(slice=0))
    r = subprocess.run((sys.executable, str(PARSER), str(log), "--out", str(d / "dup"), "--workload", "fixture", "--framework-commit", "f", "--core-commit", "c"), capture_output=True, text=True)
    assert r.returncode != 0 and "duplicate application slice" in r.stderr, r.stderr
# Keep this implementation guard close to the behavioral fixture: large raw
# logs must never require whole-file text/byte materialization for parsing or
# hashing.
source = PARSER.read_text()
assert ".read_text(" not in source and ".read_bytes(" not in source
print("EPL2MOTV1 parser regression: PASS")
