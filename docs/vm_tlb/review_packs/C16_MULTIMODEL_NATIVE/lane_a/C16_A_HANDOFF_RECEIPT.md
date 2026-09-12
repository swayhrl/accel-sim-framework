# C16 A reopened-local-preparation receipt

Status: `C16_A_LOCAL_PREP_REOPENED_WAVE1_IN_PROGRESS`.

| Role | Identity |
| --- | --- |
| C16 planning authority | `f222e66f49af56cfd4ded671c4a50c6811237cc2` |
| C16 A local artifact checkpoint | `42d12e149314d00c230ecfa9b8e9e3c39084bf5d` |
| C16 A integration artifact checkpoint | `2a06944c359a9873ae72c89015eb5235dda2d2ee` |
| C16 A integration producer checkpoint | `bf2a7535d5dd96339a63567ceb13308092db0c67` |
| Final handoff branch | `hrl/vm-c16-a-static-coord-v0` |
| Current scope | immutable Llama P0 plus ongoing C16 Wave-1 local preparation; prior partial G/C integration is historical only |

The prior `PUBLISH_MANIFEST.json` remains a historical partial-review object;
it is not authority to close the reopened work. New Wave-1 files must be local
and whole-file SHA-256 verified. The final fixed G/C/H manifests have now been
simultaneously consumed only after every named payload hash validates; their
identities are recorded in `integration/CONSUMED_C16_RELEASES.tsv`. This receipt is not a
`C16_GPU_PACKAGE_MANIFEST.tsv`, does not authorize transfer/rental, and does
not consume a live G/C/H result. The immutable Llama-only P0 package is
separately recorded under `packages/C16_GPU_PACKAGE_P0/`; it has no authority
over unfinished Qwen assets and starts no GPU workload. Reviewers must keep historical artifact
checkpoints separate from the future new artifact checkpoint and final handoff
HEAD, and must read the stage status, gap register, and cost model before
interpreting readiness.
