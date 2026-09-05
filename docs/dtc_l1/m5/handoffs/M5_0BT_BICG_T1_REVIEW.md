# M5.0BT T1 — Exact BICG V100 capture review

Status: `PASS` — exact BICG capture is immutable and archived. This is capture
evidence, not a Base/IO/OO simulator result.

| field | value |
| --- | --- |
| workload / source | `bicg` / `polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` `CUDA/BICG/bicg.cu` SHA-256 `e6a480c75f939958edd2633d7dc1be0a14d9890c6adb7b916b0db5e2c75965bd` |
| dimensions / build | `NX=NY=4096`; CUDA 11.8 `-arch=sm_70 -O2 -cudart shared`; executable SHA-256 `65d55be1dc570c6d6ec23d0deccf9ae16a97ab1471e35d740310d81ed410c39a` |
| hardware | Tesla V100-PCIE-32GB; `GPU-058aa9e4-e6ec-bb6d-3cc9-f46202658ad0`; CC 7.0 |
| tracer | pin `0db04452ec1c47630e4b08002067d82c6811e243`; tree `56a3dda534bd33fa14839bf67173e8055d816a719511c997b906ec05973fb3f6`; NVBit 1.8 archive SHA-256 `72a2b827f9531dcb86b6be13844f267640fb440929d92944177029da6da2b9e1` |
| bundle | `ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33` |
| archive | `bicg.tar.zst`, 43,146,784 bytes, SHA-256 `cdc0a9f540c85a2d43dab5ac77ccda924ddecb16c3e5ddd4f1b5c8652422f31e` |

## HARD acceptance evidence

- Source/tree/file, CUDA 11.8/sm70 build and V100 probe pass.
- Hardware checker: `source_comparison_mismatches=0`.
- Two raw `.trace` and two grouped `.traceg` files pass ordered mapping:
  all five `MemcpyHtoD` rows are byte-identical and both kernels map
  `.trace -> .traceg` positionally.
- Geometry manifest has two `(grid 16,1,1; block 256,1,1)` BICG invocations.
- Bundle `SHA256SUMS` validates after archive completion; accepted tracer
  evidence contains no CUDA/NVBit/tracer fatal or assertion.

## Byte accounting and next gate

| item | bytes |
| --- | ---: |
| raw trace set | 416,485,958 |
| grouped trace set | 305,558,210 |
| complete trace directory | 722,049,755 |
| archive | 43,146,784 |

M5-0BT-001 through M5-0BT-009 are preserved recovery evidence, not formal
results. The accepted bundle is retry-8 plus resume-only finalization; no GPU
application reran after raw/grouped/checker success. Next: BICG-bound storage
admission, copyback receipt, then same-bundle Base/IO/OO T2 qualification.
