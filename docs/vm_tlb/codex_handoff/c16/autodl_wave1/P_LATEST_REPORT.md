# C16-P local postprocess report

Status: `REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL`.

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
rows, and all 5/5/5 required NVTX ranges match. Local export is now P default.

P locally exported both reports and retained the complete 169,920 launch
population (S1 56,720; S2 113,200). The 134,253,922-byte TSV and deterministic
5,110,532-byte gzip are raw-outside-Git with SHA-indexed manifests. Operator
and layer stay `UNKNOWN`; semantic mapped-time coverage is intentionally 0.0.

Lane-C's required catalog fields and composite join identity are available:
zero empty required fields and zero duplicate
`run_id+device+context+stream+correlation_id+launch_ordinal` units.

## Requested G closeout metadata

No C join column is missing. Before C consumes a catalog, please commit:

1. the G formal native producer checkpoint and hash manifest;
2. a transfer receipt recording remote and local path/size/SHA for each raw
   report (the current remote profile receipt's output SHA is `NA`); and
3. direct mapping evidence only if non-`UNKNOWN` operator/layer or runtime-KV
   layout labels are desired.

Read the P review-pack `README.md` and
`LOCAL_NSYS_EXPORT_QUALIFICATION.md` for the full qualification and local
raw-index paths.
