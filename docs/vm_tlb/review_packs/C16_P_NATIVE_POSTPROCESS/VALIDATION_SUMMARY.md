# C16-P validation summary

| Check | Result | Evidence |
| --- | --- | --- |
| Input raw/remote-SQLite SHA closure | PASS | Both S1 and S2 hashes were recomputed and match their G `CENSUS_EXPORT_VALIDATION.json` bindings. |
| Old local CLI rejection | EXPECTED | Nsight 2022.4.2 reports `Version not supported: 33998838`; it is excluded from C16. |
| Compatible local CLI installation | PASS | NVIDIA Nsight Systems 2024.2.3.38 archive SHA is recorded in `LOCAL_NSYS_EXPORT_QUALIFICATION.md`. |
| Frozen S1 remote vs local qualification | PASS | Shared schemas equal; 56,720 kernel and correlation rows, stream `{7}`, and all required NVTX counts/overlaps equal. |
| P local-export wrapper | PASS | Its S2 receipt records the raw SHA, local SQLite SHA, tool version, and low-priority command. |
| Local S1/S2 postprocess | PASS | Both reports exported locally; catalog contains 56,720 + 113,200 = 169,920 rows. |
| Full-population preservation | PASS | No row is outside the required full-forward interval; catalog rows equal source kernel rows per run. |
| Deterministic compression integrity | PASS | Decompressed gzip has 169,921 lines (header + 169,920 data rows); full TSV and gzip hashes are in the postprocess manifest. |
| C join-key/schema audit | PASS | All required fields are populated; zero duplicate composite unit identities. |
| Event-driven run/join audit | PASS | `RUN_JOIN_AUDIT.json` checks report/run scopes, repeat keys, full populations, and report-local ID collisions. |
| Semantic non-inference | PASS | Zero catalog rows have non-`UNKNOWN` operator or layer values. |
| P utility syntax | PASS | `python3 -m py_compile util/vm_tlb/c16/lane_p/local_native_postprocess.py`. |

All large export/compression invocations were run with `nice -n 19` and
`ionice -c2 -n7`. No GPU workload or remote command was started.
