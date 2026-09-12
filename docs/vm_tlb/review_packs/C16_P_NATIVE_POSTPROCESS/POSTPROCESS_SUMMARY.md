# C16-P S1/S2 local postprocess summary

Status: `REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL`.

P exported both real, SHA-verified frozen reports locally with the qualified
Nsight Systems 2024.2.3 CLI, then built the catalog and summaries below. These
are not cross-lane scientific conclusions and must not freeze Lane C before G
commits the formal native producer checkpoint.

| Scenario | Run UUID | Local SQLite SHA-256 | Launches | Streams | Correlated launches | NVTX full/prefill/decode |
| --- | --- | --- | ---: | ---: | ---: | --- |
| S1 CODE | `eee03ffd-714e-4c66-beb0-1acd6ed45f79` | `2a7fd47486e5880a916856874207bd1c3e6c3800dff77fc5019bcf140e54e704` | 56,720 | 1 | 56,720 | 5 / 5 / 5 |
| S2 TEXT | `2a4c3b95-7357-432d-ad17-e95709752be8` | `636ef22a938db5b1e2d286fb100fa608f5d3b7a606269d8ac0d5f9e19f0afc90` | 113,200 | 1 | 113,200 | 5 / 5 / 5 |

The complete preserved population is 169,920 launches. `KERNEL_CATALOG.tsv`
is 134,253,922 B, SHA-256
`14c5d4ec87959ee4039e8993a959eefbebfca4cfddc606d10c9ad483ac9ab707`.
The deterministic gzip contains the same logical rows, is 5,110,532 B, and
has SHA-256 `a3f7cfc51db94fcecfa7321b21ed0dc255d0090a35c8b20c9adc28f9488a816b`.
Both stay outside Git; neither population nor rows were reduced for size.

Compact outputs were generated locally: 146 phase-scoped semantic-map rows,
six semantic-coverage rows, 13 provisional single-launch heavy-tail rows, six
unprofiled native-baseline measurements, two runtime-implementation audit rows,
and six phase summaries. Semantic coverage is 0.0 mapped GPU time in every
phase because no direct operator/layer evidence was supplied; all operators and
layers therefore remain `UNKNOWN`.

The raw-outside-Git index SHA-256 is
`4a72b166533856806d8b35d95bd2ab75dfb6e80189a3e8ed7cacb7ab1fd95502`; the
postprocess manifest SHA-256 is
`9a67a9fe86556f36fb1528621e53905472228ecb1bc22443c94bc4b6f996e4ef`.
Their local paths are:

`/workspace/worktrees/accel-sim-vm-c16-p/artifacts/c16_p_native_postprocess/local_exports_provisional/RAW_INDEX.tsv`

and

`/workspace/worktrees/accel-sim-vm-c16-p/artifacts/c16_p_native_postprocess/local_exports_provisional/POSTPROCESS_MANIFEST.json`.
