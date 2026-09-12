# C16-P local postprocess report

Status: `C16_P_EVENT_DRIVEN_NATIVE_POSTPROCESS_ACTIVE`.

Current fixed P baseline before this event: `70a8191ef264d91db561115e25e57da953420f94`.
P now holds an active eight-hour event-driven local CPU role. It polls the G
remote branch only for a changed remote HEAD, consumes only hash-closed P1/P2/P3
events, commits/pushes each completed model/scenario batch, and never creates an
empty commit during a quiet interval.

P initially found two formal, SHA-bound Llama reports:

- S1 CODE run `eee03ffd-714e-4c66-beb0-1acd6ed45f79`, raw SHA
  `0aff1fd0c2155527955dab34aaa605135ae9cc103e307ed1353a1cde8eb87364`;
- S2 TEXT run `2a4c3b95-7357-432d-ad17-e95709752be8`, raw SHA
  `5a602bf2aec7700c5f3efb742ccd86fdc59bb37f17cdb228dae01ab0d6042bf0`.

Both match the relevant `CENSUS_EXPORT_VALIDATION.json` raw-profile SHA, and
their remote-export SQLite SHA bindings also matched locally. Local Nsight
2022.4.2 cannot read the reports; P installed a compatible local 2024.2.3 CLI.
Paired S1 remote-versus-local qualification passed: shared schemas, 56,720
kernel rows, stream `{7}`, 56,720 CUDA correlation joins, 113,397 NVTX overlap
rows, and all 5/5/5 required NVTX ranges match. The frozen qualification is
`LOCAL_NSYS_EXPORT_QUALIFIED_FOR_CURRENT_TOOL_PAIR`; local export is P default
until a material tool/schema/command/consumed-field change requires recheck.

P locally exported both reports and retained the complete 169,920 launch
population (S1 56,720; S2 113,200). The 134,253,922-byte TSV and deterministic
5,110,532-byte gzip are raw-outside-Git with SHA-indexed manifests. Operator
and layer stay `UNKNOWN`; semantic mapped launch and GPU-time coverage are
intentionally 0.0, while UNKNOWN duration is explicitly retained.

Lane-C's required catalog fields and composite join identity are available:
zero empty required fields and zero duplicate
`run_id+device+context+stream+correlation_id+launch_ordinal` units. The
event-driven join audit additionally found 4,501 correlation-ID collisions and
the same stream (`CUDA_STREAM_7`) across reports, so P prohibits unscoped
stream/correlation joins. Baseline repeats are separate scenario measurements,
not multiplied launch populations.

## Llama S2 P2 event consumed

G subsequently committed the passing Llama S2 direct-semantic diagnostic at
`64f9ea0f00c2a97eedb4cc21d3d38e2b294be736`. P verified its producer manifest,
receipts, raw report, remote SQLite, and G direct map hashes; locally re-exported
the frozen `.nsys-rep`; and independently reproduced all 45,280 diagnostic map
rows with zero mismatches. The P2 outputs are committed as compact receipts;
large maps remain outside Git.

P's clean↔diagnostic map retains all 113,200 clean S2 launches, but its strict
report-scoped structural join produced 111,223 multi-candidate rows and 1,977
zero-candidate rows. All clean rows therefore remain `UNKNOWN`, with
`COVERAGE_LIMITED` status. This result is intentional: no timestamp,
correlation, stream, duration, launch-ordinal, or kernel-name semantic guess was
used across reports. See `P2_LLAMA_S2_DIRECT_SEMANTIC_POSTPROCESS.md` and
`P2_LLAMA_S2_SEMANTIC_RECEIPT.json`.

## Requested G closeout metadata and next event

No C join column is missing. Before C consumes a catalog, please commit:

1. the G formal native producer checkpoint and hash manifest;
2. a transfer receipt recording remote and local path/size/SHA for each raw
   report (the current remote profile receipt's output SHA is `NA`); and
3. direct mapping evidence only if non-`UNKNOWN` operator/layer or runtime-KV
   layout labels are desired.

`P_TO_G_SCHEMA_REQUEST.md` states the exact P1/P2/P3 fields. P has consumed the
G P2 diagnostic producer checkpoint above, but no C-consumable multi-model
native-catalog checkpoint exists yet. The initial clean-profile receipts record
runtime code commit `12e9f16d1e503d3b4bfeba0fa08e0d350669f0e2`.

The next expected event is a hash-closed P1/P2/P3 receipt. P prioritizes
Qwen0.5, Qwen7 raw, then Qwen7 AWQ. AWQ output will remain
`HOLDOUT_PENDING_FREEZE` and will not be supplied to C before C publishes its
selector-freeze SHA. A deployment explicitly declared `BLOCKED` or
`SKIPPED_RESOURCE` is logged and skipped without ending P's event loop.

Read the P review-pack `README.md`, `JOIN_KEY_CONTRACT.md`,
`EVENT_INPUT_CONTRACT.md`, and `LOCAL_NSYS_EXPORT_QUALIFICATION.md` for the
full contracts, qualification, and local raw-index paths.
