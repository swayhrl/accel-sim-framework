# C16-P local postprocess report

Status: `C16_P_LOCAL_POSTPROCESS_READY_WAITING_G_SEMANTIC_OR_NEW_PROFILE`.

Current P evidence checkpoint: `5a90f9537f3dd7f8a9cc62113fd934ceb2260649`.
It is an event-driven local CPU lane: P is not holding an active Goal while it
has no complete P1/P2/P3 input. The preceding local-export/postprocess
checkpoint `0f7baac672614f39bbc0464555587c667e7db61d` was pushed and its remote
head was verified before this milestone.

P found two formal, SHA-bound Llama reports:

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

## Requested G closeout metadata and next event

No C join column is missing. Before C consumes a catalog, please commit:

1. the G formal native producer checkpoint and hash manifest;
2. a transfer receipt recording remote and local path/size/SHA for each raw
   report (the current remote profile receipt's output SHA is `NA`); and
3. direct mapping evidence only if non-`UNKNOWN` operator/layer or runtime-KV
   layout labels are desired.

`P_TO_G_SCHEMA_REQUEST.md` states the exact P1/P2/P3 fields. No committed G
formal producer checkpoint has yet been consumed; the available profile receipts
record runtime code commit `12e9f16d1e503d3b4bfeba0fa08e0d350669f0e2`.

The next expected event is either a hash-closed P1 report or a P2 direct
semantic diagnostic. P will not notify C to freeze a prospective selector from
the current all-UNKNOWN semantic census.

Read the P review-pack `README.md`, `JOIN_KEY_CONTRACT.md`,
`EVENT_INPUT_CONTRACT.md`, and `LOCAL_NSYS_EXPORT_QUALIFICATION.md` for the
full contracts, qualification, and local raw-index paths.
