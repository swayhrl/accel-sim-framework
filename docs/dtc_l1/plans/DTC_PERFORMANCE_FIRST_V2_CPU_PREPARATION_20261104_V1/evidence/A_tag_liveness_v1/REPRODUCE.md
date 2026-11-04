# CPU-only replay

Select a currently legal, low-pressure CPU without changing any existing task affinity. The recorded execution used CPU128 at nice19; that historical choice is not permission to compete with a newly active model. Supply a new true164 output directory that does not exist:

```sh
python3 -B <packet>/RUN_CPU_FIXTURES.py --source-root <packet> --output-root /root/share/mnt164/huangrulin/host174_storage_recovery/<new-private-cpu-replay> --cpu <legal-id>
```

Requires existing g++ and Python3; no package installation. The script uses one CPU, nice19, 2GiB virtual-address limit, 60s per-child CPU limit, no core dumps and true164 TMPDIR/TMP/TEMP. Expected assertion deaths are isolated fixture children, not simulator signals. Outputs include per-header JSONL/stdout/stderr/compile logs, compiler argv, CPU replay result and private binaries; delete/move nothing in V1. Expected case executions: original22, prototype24. Check source SHA and the frozen manifest before reuse. No performance cycles or application numerical results are produced.

`CPU_EXECUTION_RESULTS.json` is the actual original run, not the replay script syntax check. `SOURCE_EVIDENCE.json`, `SOURCE_BINDINGS.json`, and the patch bind the tested code. All report claims remain conditional as stated in A_TAG_LIVENESS_AND_DESIGN.md.
