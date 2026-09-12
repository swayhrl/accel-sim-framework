# C16 A reopened-local-preparation receipt

Status: `C16_A_WAVE1_ROLLING_PACKAGES_P0_TO_P3_PUBLISHED`.

| Role | Identity |
| --- | --- |
| C16 planning authority | `f222e66f49af56cfd4ded671c4a50c6811237cc2` |
| C16 A local artifact checkpoint | `42d12e149314d00c230ecfa9b8e9e3c39084bf5d` |
| C16 A integration artifact checkpoint | `2a06944c359a9873ae72c89015eb5235dda2d2ee` |
| C16 A integration producer checkpoint | `bf2a7535d5dd96339a63567ceb13308092db0c67` |
| Final handoff branch | `hrl/vm-c16-a-static-coord-v0` |
| Current scope | immutable Wave-1 transfer deltas P0--P3 are published; Wave-2 remains background asset supervision only; prior partial G/C integration is historical only |

The prior `PUBLISH_MANIFEST.json` remains a historical partial-review object;
it is not authority to close the reopened work. New Wave-1 files must be local
and whole-file SHA-256 verified. The final fixed G/C/H manifests have now been
simultaneously consumed only after every named payload hash validates; their
identities are recorded in `integration/CONSUMED_C16_RELEASES.tsv`. This receipt is not a
`C16_GPU_PACKAGE_MANIFEST.tsv`, does not authorize transfer/rental, and does
not consume a live G/C/H result. The immutable P0--P3 package directories are
separately recorded under `packages/`; P2 binds raw Qwen2.5-7B at
`a09a35458c702b33eeacc393d103063234e8bc28` and P3 binds Qwen2.5-7B-AWQ at
`b25037543e9394b818fdfca67ab2a00ecc7dd641`. Each includes its own manifest,
expected hashes, transfer plan, frozen input/token/scenario bindings, and the
fixed G/C/H commit-plus-manifest identities. They are transfer-only artifacts
and start no GPU workload. Reviewers must keep historical artifact
checkpoints separate from the future new artifact checkpoint and final handoff
HEAD, and must read the stage status, gap register, and cost model before
interpreting readiness.
