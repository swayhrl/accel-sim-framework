# E1 RAW down_proj Authority Recovery V2

The second STOP is a genuine provenance mismatch for the historical E1 RAW `down_proj` points. Do not continue the RAW_FP16 bridge yet.

## Important correction

Do **not** use `/data/c16/v9_raw_module_state.pt` as a required cross-check against the E1 prefill M1 slice.

The accepted V10 semantic pair is explicitly a **DECODE** `mlp.down_proj` state:
- layer 0
- decode token 23578
- shape `[1,1,18944]`

Therefore a V9/V10 decode-state input being different from the E1 prefill-derived M1 input is expected and is not itself an authority failure.

The real unresolved issue is:

> V8 exact-stream reconstruction reproduces historical q_proj M1/M256 output SHAs but does not reproduce historical down_proj M1/M256 output SHAs.

This means V8 exact-stream is not yet proven to be the historical E1 RAW down_proj source.

## Historical E1 contract to recover

The accepted AWMA E1 V2 execution contract defined RAW authority as:

- RAW model: `Qwen/Qwen2.5-7B-Instruct`
- revision: `a09a35458c702b33eeacc393d103063234e8bc28`
- token SHA:
  `0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`
- live Layer0 module hooks on the natural M2048 execution
- M256 = first 256 rows
- M1 = first row
- shape-specific direct RAW module oracle

Historical output SHAs:

- q_proj M256:
  `6c662b748af24fd67f1871b1a71c7ef134e5b7dd3e7b6d043b0ee32780873c21`
- q_proj M1:
  `b573d074433dd5fb43314fc82a43697ea93c6c7f0016df7faaa32522bf11ddb4`
- down_proj M256:
  `962e2846f8e999bebc3d979d1e73c71e947ddc27c1e9e280d32039a1436c3007`
- down_proj M1:
  `0af0c81eee41d0f1d5aceb7f7d28452c548956a3f4fb4d352ae772f0e6cf4671`

## Bounded recovery procedure

Do not try arbitrary inputs/runtimes.

Recover provenance in this order:

1. Search local node109 C16/AWMA artifacts and historical worktrees for the exact E1 V2 RAW runner, activation tensors, or receipts.
2. Search node164 through the accepted network path `109 -> hrl174new -> /root/share/mnt164/huangrulin/` for E1 V2 RAW activation/raw-data artifacts that may have been published but omitted from the Git review pack index.
3. If the exact historical runner/source is found, rerun only the RAW Layer0 natural M2048 replay and regenerate q_proj/down_proj M256/M1 slices.
4. If no runner file survives, a reconstruction from the frozen historical contract above is acceptable only when one single replay path reproduces **all four historical RAW output SHAs** under one consistent runtime/source identity.

Record for the recovered replay:
- model root/revision
- token path/SHA
- torch/transformers versions
- module source SHA if available
- full-model/replay entrypoint
- q_proj M2048 input tensor SHA
- down_proj M2048 input tensor SHA
- M256/M1 slice tensor SHAs
- four direct output SHAs

## PASS gate

Authority recovery PASS requires one consistent provenance path that reproduces all four historical output SHAs.

Then:
- freeze all four RAW activation authorities durably;
- write a recovery receipt;
- continue the existing E1 RAW_FP16 bridge.

## FAIL gate

If no accepted/durable historical provenance path reproduces all four SHAs:

- mark the old eight-point E1 RAW side as `HISTORICAL_MEASUREMENT_INPUT_AUTHORITY_NOT_REPRODUCIBLE`;
- do not use those eight points as the primary causal/controlled E1 basis;
- STOP for a redesigned E1 baseline under a new explicit authority contract.

Do not silently choose V8 or V9 as the winner.
