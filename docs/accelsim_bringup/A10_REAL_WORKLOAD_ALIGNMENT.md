# A10 Real Workload Alignment

A10 converts the A9 Mascar/MeDiC template into a real, evidence-backed alignment pass.

The phase order is fixed:

```bash
bash scripts/accelsim/a10a_discover_prior_workflows.sh
python3 scripts/accelsim/a10b_extract_prior_inventory.py
python3 scripts/accelsim/a10c_build_trace_mapping.py
ACCELSIM_A10D_DRY_RUN=1 bash scripts/accelsim/a10d_run_aligned_smoke.sh
bash scripts/accelsim/a10d_run_aligned_smoke.sh
bash scripts/accelsim/a10e_collect_alignment_pack.sh
```

`scripts/accelsim/a10_run_all.sh` runs the same order and refuses to start if `git status --short` is not clean.

A10 is bounded. It reads prior repos under `/workspace/repos`, extracts workload and stats evidence, maps only to existing `kernelslist.g` traces, and runs at most a small aligned smoke set. It does not validate NVBit tracer and does not run a full paper reproduction campaign.
