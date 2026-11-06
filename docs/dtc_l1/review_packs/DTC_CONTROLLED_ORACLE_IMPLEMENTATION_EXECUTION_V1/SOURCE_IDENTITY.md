# Frozen source and build identity

| Identity | Exact value |
|---|---|
| Authority | 18b1ee9d339902e555fc2e04ef51c84f77dfe1b1 |
| Original Core | 9eedb3131937748f0492fa83aad37d3691118d70 |
| Isolated Oracle Core | [e6b41ab8992e7d41651501c4d34cfe24195c4f96](https://github.com/swayhrl/gpgpu-sim/commit/e6b41ab8992e7d41651501c4d34cfe24195c4f96) |
| Framework | 02775fd795cde5aae1480d81cee6eb481d0a08f4 |
| Executable SHA256 | 3f8e547d87893aaf7319e337883a2bcc1f5717138296e3e6d1425cc75d055283 |
| libcudart SHA256 | 174f53a02223ae69e4a549e60a310f7e69a9334748e719fd48c40640c2a0af43 |
| Source-delta SHA256 | 03d1dfa5a0733ce5ee91cbefcdac094aca310ce26a0bc34ff570bbfe0df6eb86 |

Platform:SM70/V100-derived64SM,10MiB L2,DRAM850MHz, unchanged other clocks and original270 DH-P0 options plus one Oracle enum. All modes share one immutable build. Actual OFF must match executable/library, full input and configuration identity; historical DH-P0 cannot replace it.

SOURCE_IDENTITY.json pins the source/build freeze, component CPU manifests and independent reviews. Binaries, libraries, raw traces and model logs are not publication payloads. Source/binary changes after a real start require explicit identity reconciliation, never silent reuse of a consumed row.
