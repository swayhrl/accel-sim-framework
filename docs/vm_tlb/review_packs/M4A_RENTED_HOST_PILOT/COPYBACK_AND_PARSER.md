# Copy-back and parser status

Copy-back target: `/workspace/m4a-rented-host-pilot/` on the main development
server. `rsync --partial` copied P1/P3/P4 evidence from the remote data mount.

Verified source/destination SHA256 values:

| Artifact | SHA256 |
| --- | --- |
| `generic-nvbit-smoke.tar.gz` | `0b369d661b5b106d40c29a623365794d2dadb36bdb8666e5c46b447f2a0522eb` |
| `capture-ready-preflight.json` | `1f70495c36289a0c4736f48cebdd4621892f6b090f11b698094a0d10252cdb2f` |
| `host-preflight.json` | `5e5966f92b6b9f73e25b6e382471bf3674e061114fdce85f81582485f944195a` |

The copied generic `kernelslist.g` was reclassified locally without modifying
the raw list. It has one `COMPUTE` entry and produces the full manifest plus
compute-only derived list. This is an integrity/classifier smoke only.

The frozen simulator trace parser was not run: P6 produced no Llama pilot
bundle, so a parser result would not satisfy its compatibility objective. No
Core M1–M3 code or NCCL policy was changed.

## Repaired local-snapshot pilot evidence

The checksum-verified diagnostic bundle was copied to
`/workspace/m4a-rented-host-pilot/r4-diagnostic-decode1/`:

| Artifact | SHA256 |
| --- | --- |
| `m4a-llama-decode1-20260902T171148Z.tar.zst` | `291dcc3c21ba29579842dd5897995c52887625caaa3342f0f75758242b8bcf98` |

The remote and main-server digests are equal, as recorded in the bundle's
`COPYBACK_VERIFICATION.md`. The small R3 four-rank workload/sidecar evidence is
also retained at `/workspace/m4a-rented-host-pilot/r3-p5-local-smoke-final/`.

For parser compatibility, the frozen Core
`73774727e25fadf89df6f30ef5cf014091115db7` and the SM86 RTX 3070 trace
configuration were used only as a parser smoke. The 75-second bounded run
initialized the performance model and parsed/started 35 real SM86 trace
kernels; no trace-format, unsupported-binary-version, or parser fatal error
was observed. This is not a performance result and does not claim that the
RTX 3070 configuration represents the captured RTX 3080 Ti hardware.
