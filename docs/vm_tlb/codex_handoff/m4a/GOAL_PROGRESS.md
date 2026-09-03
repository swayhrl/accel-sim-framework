# M4A-C Goal progress

Goal: `M4A_C_FORMAL_CAPTURE`

## Power-loss recovery record

`INFRASTRUCTURE_INTERRUPTION / AUTO-DL_BALANCE_SHUTDOWN`: the rented instance
was powered off after the formal prefill archive had completed and its
source/destination SHA256 had matched. It is not a failed prefill experiment.
The authoritative persistent checkpoint is
`/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`.
On 2026-09-03, its SHA256 was independently rechecked as
`f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181` and its
zstd/tar listing test passed. It must not be recaptured.

| Gate | Status | Framework source SHA | Evidence / next action |
| --- | --- | --- | --- |
| G0 | PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Pilot admission remains valid. After power-on, host `autodl-container-y3dnxs4rbm-7ddc7538` has four idle homogeneous RTX 3080 Ti SM86 GPUs, driver `595.71.05`, 970 GiB free on retained `/root/autodl-tmp`, and no stale capture process. |
| G1 | PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Restart sanity: Python 3.10.12, torch 2.6.0+cu126/runtime 12.6, selected CUDA 12.6 nvcc/ptxas, local six-file snapshot SHA256/size check, and capture-ready preflight all pass. Rank0-only wrapper hashes match the lock. |
| G2 | FORMAL PREFILL PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Run `m4a-llama-prefill-20260902T182016Z`: 724 raw and 724 postprocessed traces; FORMAL/BF16/TP=4/B8/S64/G3, rank0-only NVBit. Archive SHA256 is the authoritative G3 checkpoint. |
| G3 | PREFILL COPYBACK PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Local archive exists, exact SHA256 matches remote, and archive integrity passed. Infrastructure shutdown occurred only after this durable checkpoint. |
| G4 | PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Formal decode1 `m4a-llama-decode1-20260903T004138Z`: TP=4/B8/S64/G3/BF16/rank0 NVBit, 772 raw + 772 traceg. |
| G5 | PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Archive copied to `/workspace/m4a-rented-host-pilot/formal-decode1/`; remote/local SHA256 `5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`. |
| G6 | PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Both bundles archive/internal-manifest validated; Weight=1, real KV=128, no synthetic KV; raw/full lists retained. |
| G7 | PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Frozen Core SM86 parser bounded smoke bound first ordinary compute kernel for both formal lists; compute-only equals full list. |
| G8 | PASS | `c79f4469c6a2befa59e4c4efcd3c885dc2259a81` | Review evidence and storage capacity model updated; ready for ChatGPT review after push. |

## Pilot evidence retained on the main server

- R3/P5 four-rank real TP4 evidence:
  `/workspace/m4a-rented-host-pilot/r3-p5-local-smoke-final/`
- R4/P6 diagnostic archive and checksum record:
  `/workspace/m4a-rented-host-pilot/r4-diagnostic-decode1/`

The diagnostic decode1 trace is not formal evidence.
