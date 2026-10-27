# Independent incremental L2-MLP report

Run once, read only, then exit:

```sh
python3 /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/D/report_v1/build_report.py \
  --root /root/data/dtc_l2_mlp_exploration_20261027_v1 \
  --output /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/D/report_v1/current \
  --tool-commit <commit-containing-this-generator>
```

The commit argument is optional before publication: the generator records its complete SHA and explicitly says uncommitted. After publishing its source, pass that source commit. No service, controller or model is started. The output directory must be outside the live experiment root. No production modules are imported or changed.

Generated files: `dashboard.html`, `report.json`, `sensitivity.png`, `sensitivity.svg`, `REPORT_MANIFEST.json`. Artifacts are approximately 1 MB for the current partial matrix. Matplotlib dependencies are isolated in `.python-deps` on 164; exclude that directory and `.windows-deps` from review packages.

The report reads coherent individual file snapshots and records source path, SHA and size. It does not claim a transaction spanning all independently changing files. Recalculated GMs are checked against the existing summary only where populations match.

`RUNNING_CONFIRMED` requires a native PID identity receipt bound to the same INTENT, matching current `/proc` PID/start ticks, command line, executable and mount namespace. The process start time is read twice and zombie/dead states are rejected. A dispatch slot alone is `RUNNING_UNVERIFIED`; a spent identity with absent/mismatched PID evidence stays `SPENT_*_AWAITING_TERMINAL`. Terminal receipts awaiting acceptance are shown separately. The report never treats controller membership as proof of a live model. These observations are timestamped and do not assert forward progress or predict future liveness.

Each uniform profile has its own explicit paired population. Common four-cell results and the fixed intersection across **all** registered non-P0 profiles are also included. Missing P0, missing matched CH, failures and pending points are not zero-filled. Failed points retain their states and any raw reported cycles but never enter performance statistics. No per-program best configuration is used.

The `input_stream_scope.json` evidence covers all 35 inputs and 7,368 qualified kernel headers: all inputs are single-stream, although stream ID may differ between inputs. Full per-header evidence is compressed in `input_stream_scope_full.json.gz`, with both compressed and uncompressed SHA recorded in the compact file. L2 buckets are per-stream cumulative; last-printed values are declared-trace totals for these verified single-stream inputs. Missing MSHR reasons remain missing. DRAM counters are globally cumulative. Trace acceptance does not prove numerical correctness of a whole application.

Structure counts are capacities/upper bounds, not physical area, occupancy or free hardware. Fixed L2 capacity, DRAM850 and DTC architecture are preserved. FR-FCFS window changes also affect memory-partition credits.

`test_report.py` provides analytical GM/median and coverage fixtures, negative and failed-result handling, missing denominators, common-population arithmetic, six-proof P0 reuse, stream-scope withholding, structure counts, source hashing and empty/partial chart rendering. All tests are CPU-only.
