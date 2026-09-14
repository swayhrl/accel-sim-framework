# TC80 controller genealogy

Every simulator attempt copies its runner into its own immutable directory and
records its SHA-256 in `RUN_MANIFEST.tsv`. This record makes the small
controller-only corrections auditable without rewriting an earlier receipt.

| runner SHA-256 | affected attempts / use | change and disposition |
| --- | --- | --- |
| `2fe95e177a659dc3029c5ee23f50908f1128349899c08bcaa0c6b8895f26eabe` | first CM2 NN attempt only | Controller passed relative config paths after changing to an isolated attempt directory. The simulator rejected the missing config and exited 1; raw output is retained, never accepted. |
| `0ac1f4792272eef1e4ecc92578466672a8816682de4bf8ec29169d3bc210e2a1` | accepted CM2 NN and Btree; live CM2 BICG | Minimal path-resolution correction: resolve frozen configs before changing cwd. No simulator, Core, trace, option, or scientific semantic changed. |
| `06b22f4f911cb0a3d6b7067bfc7b54426a2f92c4d23412cd3397b3e7355b6926` | future CM3 primary and CM5 diagnostic attempts only | Adds two closed geometry profiles, `TC80_S32_W20` and predeclared `CM5_S128_W5`, plus a manifest-geometry strict check. The canonical default remains 32×20×128 = 640 lines = 80 KiB. |

The accepted CM2 BICG attempt remains bound to the second hash above. Future
primary attempts will use one common immutable copy of the third hash, so CM3
has one controller epoch. The profile extension was unit-checked by isolated
revalidation of the existing Btree raw output; that revalidation was written
outside the attempt directory and did not overwrite its accepted receipt.
