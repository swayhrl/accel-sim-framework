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
