# M5.0BT — Exact 2DConv heavy storage-fidelity pilot

Status: `PASS` for the required heavy-pilot storage update and immutable-store
copyback. This is capture/storage evidence only; it is not a formal replay
result and does not advance M5.0BT past T2.

| item | evidence |
| --- | --- |
| source / input | `polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c`, `CUDA/2DCONV/2DConvolution.cu`, SHA-256 `cef6d23d7c1d931e5427175dcf4c02a2d5e81ca2747b133222ad962d63b390d8`; frozen `NI=NJ=4096` |
| exact capture | V100 CC 7.0, CUDA 11.8/sm70 executable SHA-256 `98eab794d1c885d1f107768968e79010fb270e71724e0cb76fb0ff259f15f0a7`; frozen tracer source tree `56a3dda534bd33fa14839bf67173e8055d816a719511c997b906ec05973fb3f6` |
| checker | `conv2d`: `source_comparison_mismatches=0` |
| stream / geometry | one raw and one grouped trace; one `_Z20convolution2D_kerneliiPfS_` invocation; `(128,512,1) x (32,8,1)` = 65,536 CTAs |
| immutable bundle | `bd5ac5f729bdad3ad24d9a405d7eff9cd54d8e060b70f206f91bc0030e1f06ee`; raw set `fd30c757e328370607974f9a58a0f8008ac78746537fc679d68ef4fd643def42`; traceg set `d165c614c090a4fa02c824864c7b4e7eb57501fa6de4fbabedb457b2e60d77fd` |
| byte measurements | raw 1,649,354,651; grouped 1,118,271,555; complete payload-file working set 2,767,658,899; archive 191,057,936 bytes |
| archive / copyback | archive SHA-256 `c7bb59ef2d3a262a7d24885e215a66e3d2a00647b90002cea1bf16e0a8658a02`; destination SHA equal; unpacked once in the immutable store and internal `SHA256SUMS` revalidation `PASS` |

## Updated storage admission

BICG's two small-grid invocations were not used as the upper-bound proxy. The
new source-exact heavy pilot instead has 65,536 CTAs. At the measurement,
101,566,291,968 bytes were free on the capture data volume. The updated
`STORAGE_ADMISSION.json` projects ten Paper payloads at twice the heavy working
set: `2,767,658,899 * 10 * 2 = 55,353,177,980` bytes. The projection is below
the measured free space, so the remaining sequential Paper capture queue is
admitted. It is a capacity guard, not a performance choice.

The accepted local transfer receipt binds the bundle ID and archive SHA with
`TRANSFER_PASS`. Neither this pilot nor the admission changes BICG's immutable
payload, T2's same-bundle requirement, formal platform settings, or any
execution-driven historical result.
