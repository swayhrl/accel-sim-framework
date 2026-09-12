# C16-P local Nsight Systems export qualification

Status: **PASS** — local export is the default for subsequent C16 `.nsys-rep`
reports received through the hash-closed P input contract.

This qualification is an export-pipeline result, not a cross-lane scientific
conclusion. All downstream S1/S2 material remains
`REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL` until G commits its formal native
producer checkpoint and output manifest.

## Frozen paired input

- Scenario/run: Llama S1 CODE,
  `eee03ffd-714e-4c66-beb0-1acd6ed45f79`.
- Frozen report: `CENSUS_S1_CODE.nsys-rep`, 8,609,301 B,
  SHA-256 `0aff1fd0c2155527955dab34aaa605135ae9cc103e307ed1353a1cde8eb87364`.
- G remote SQLite: 24,125,440 B,
  SHA-256 `9f0338957f5e65c33088562ba5b1b475e9d1d73837842b24bf8a41e8e6c61f9d`.
- P local SQLite: 24,170,496 B,
  SHA-256 `2a7fd47486e5880a916856874207bd1c3e6c3800dff77fc5019bcf140e54e704`.

The report and G remote SQLite SHAs are bound in the source
`CENSUS_EXPORT_VALIDATION.json`; P recomputed both locally before use.

## Tool provenance

- Remote export tool: user-confirmed AutoDL Nsight Systems `2024.1.1.0-90`.
- Local CLI: Nsight Systems `2024.2.3.38-242334140272v0`.
- Local archive: NVIDIA `nsight_systems-linux-x86_64-2024.2.3.38-archive.tar.xz`,
  SHA-256 `36b457ec34572699c7ddba94aec659a02d4ec78fe19bec7750918fd7e9b79119`.
- The installed local executable exported the frozen report without GPU access.
- The pre-existing local Nsight 2022.4.2 rejected that report with
  `Version not supported: 33998838`; it is not used for C16 exports.

## Field-level comparison

| Check | Remote export | Local export | Result |
| --- | ---: | ---: | --- |
| CUDA kernel/activity rows | 56,720 | 56,720 | Equal |
| Named kernel rows | 56,720 | 56,720 | Equal |
| Stream identity | `{7}` | `{7}` | Equal |
| CUDA runtime-correlation coverage | 56,720 | 56,720 | Equal |
| NVTX kernel/range overlaps | 113,397 | 113,397 | Equal |
| `C16_NATIVE_FULL_FORWARD` ranges | 5 | 5 | Equal |
| `C16_PHASE_PREFILL` ranges | 5 | 5 | Equal |
| `C16_PHASE_DECODE` ranges | 5 | 5 | Equal |

The profile/binding identity also agreed on run UUID, deployment, model and
tokenizer revisions, scenario, input SHA, implementation, dtype, and package
binding. The structured qualification receipt is stored outside Git at
`artifacts/c16_p_native_postprocess/qualification/LOCAL_NSYS_EXPORT_QUALIFICATION.json`.

## Schema comparison and decision

The remote SQLite has 71 tables and the local SQLite has 79. The schemas of
all shared tables are exactly equal, including the four consumed tables:
`CUPTI_ACTIVITY_KIND_KERNEL`, `CUPTI_ACTIVITY_KIND_RUNTIME`, `NVTX_EVENTS`,
and `StringIds`. The local export has eight additional unconsumed
analysis/diagnostic tables; it has no missing remote tables and no changed
shared-table schemas. SQLite byte identity is therefore not required.

The equality of the consumed schema and all consumed row relationships passes
the C16 qualification contract. P may export future hash-closed reports with
the recorded local 2024.2.3 CLI, using the same `nice`/`ionice` policy; report
input SHA verification and per-run source receipts remain mandatory.
