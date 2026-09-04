# Embedded-header semantic kernel classification

`kernelslist.g` records opaque trace filenames. For every kernel entry, the
offline classifier opens its `traceg` file and requires exactly one embedded
`-kernel name = ...` header. Direct Memcpy entries are classified directly;
missing, malformed, or duplicate headers are `UNKNOWN_OTHER`, never silently
COMPUTE. Full/raw ordering remains untouched.

| ROI | Raw entries | COMPUTE | NCCL_COLLECTIVE | MEMCPY | UNKNOWN_OTHER | Unique compute / NCCL names |
|---|---:|---:|---:|---:|---:|---:|
| prefill | 724 | 692 | 32 | 0 | 0 | 27 / 1 |
| decode1 | 772 | 740 | 32 | 0 | 0 | 26 / 1 |

The observed NCCL family in both ROIs is
`_Z40ncclDevKernel_AllReduce_Sum_bf16_TREE_LLP11ncclDevCommmP8ncclWork`.
Prefill NCCL indices are 38, 53, then alternating every 15 through 713; decode1
indices are 41, 56, then alternating every 15 through 761. Thus old
filename-only claims of 724/772 COMPUTE and zero NCCL are superseded, not
reused.

## Reproducible derivatives

| ROI | Semantic full SHA256 | Compute-only SHA256 | NCCL-only SHA256 |
|---|---|---|---|
| prefill | `ee53ca249cd45e2fd4da6920db4038673636960d6f36f2f99789062412636908` | `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` | `9c899cd5312a8854e027db4c3415b934dfc0e9fd5e4a68c3d79a21055e978111` |
| decode1 | `9bb152d8475f7827e58071a7f765b2b00c5a2d08161a306f9031ff00a8f48701` | `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` | `c642daa4902c4d686e77934f2c9416a883ae170ccf5d18e67f86d6871ca84657` |

The generated files live under `/workspace/m4a-merge-prep/{prefill,decode1}-semantic/`.
Their source raw-list hashes are respectively
`1ac8a5c2496491be41af6305673b34a661175c15754a438fc740ca2d2449c971` and
`734674fa079cfc72ae1ea9b78bd7d31e86179612e21f7a6b5eba94e86ad3fd72`.
The command records have SHA256
`8b9705d94b4d25dbc89afb7afa6bcb855d1ca0ff5a0509aeed9c29eafdb9e0fa` and
`1ba48cd1722a370998a7c5570783147e8fc56a5eab648e34df69b50eab532519`.
