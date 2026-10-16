# Lane 4 review_r5 — exact source adaptation and current-authority runner

Consumed r4 then r5 at coordination `77a9fbe937ea23465cf0d0076d2df1909f52d055`.
Original science remains `6c136e2a56a008695f8c8b815723bf8f1a760db9`.
This continues the existing Lane4 branch, without another Goal or worker.

Completed: exact private-index ideal replay on Lane1 Core
`62dc1d179b5516e68b21b695c7a9c5d0667e9671`, two separately reviewable fixes,
V2 scientific-authority integration and 66 passing Python tests. No compiler,
build lease, simulator or cleanup was invoked. All 18 R1.1 cells remain NOT_RUN.
There is no repaired runtime source/binary/config/trace identity in this pack.

The source replay has zero conflicts and round-trips to tree
`a8a8aeafa5487f52062d16be1524da3c7489da1e`. This tree is an **uncompiled
candidate**, not a Core release or qualification. The standalone duplicate
accessor fix can be reviewed by Lane1 without integrating ideals or waiting
for Lane4. See REVIEW_FINDINGS.md for the remaining host-reference scope issue.

Runner tooling source: `b8c6cee15351b7a2dce1ccc4e4278f4a8a2bcb71`.
CONSUMED_TOOL_CLOSURE pins Lane5 runner and acceptance source bytes while
retaining its original registry authority and lock. New mode authorization is
required for both OFF and the requested ideal vector. Current fetched V2
evidence rejects all six withdrawn old COMPLETE_VALID rows; it has zero launch
authorizations and zero currently accepted application rows.

R1_1_PREPARATION.json checks the real overlays for four workloads × OFF,
I_WB, I_META, I_READ_HIT, plus I_WB_META for convolution and FWT only. Baselines
remain Lane5-owned, ideals Lane4-owned. It is explicitly non-executable; absent
identities, keys and metrics are null. A later executable spec must derive from
Lane5's same-R1.1-binary B16 spec and pass current release/vector authorization,
independent repair + applicable ideal gates, deduplication and live admission.

48GiB applies to formal production admission, not these small source/Python
tasks. Lane1's R0.1 and Lane5's B16/U_WB16 take priority. No space alternative
or threshold change is proposed by Lane4. LIVE_CHECK records no active EP-L2
lease/run and zero Lane4 simulators; seven live simulators belong to DTC-L1
based only on /proc executable/cwd metadata. They were left untouched.

PRESERVATION verifies 83 files in four frozen review packs and all nine
previously indexed raw logs + execution receipts unchanged. Old R0/R1 remain
scientifically withdrawn. Old STATIC 1.721x remains historical only; no shadow
WBUF, MSHR256 or ideal result is promoted to a complete ceiling.

Reproduce low-resource preparation, using new output directories:

```sh
python3 util/ep_l2/prepare_ft_lane4_r0_1_static.py --core /workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane4-v1 --out /tmp/lane4-new-static-audit
python3 util/ep_l2/prepare_ft_lane4_grid.py --out /tmp/lane4-new-grid.json
python3 -m unittest discover -s util/ep_l2/tests -p 'test_ft_lane4_*.py' -v
```

This replay writes only isolated Git index/blob/tree objects and its named
output directory. It does not switch a branch or modify any Core worktree.
SHA256SUMS binds every pack artifact except itself.
