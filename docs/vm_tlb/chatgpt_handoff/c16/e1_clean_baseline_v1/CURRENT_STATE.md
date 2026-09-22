# C16 E1 Clean Baseline — Current State V1

## Why a clean baseline is now required

Historical E1 RAW/AWQ timing points remain useful as **historical deployment measurements**, but the RAW input authority used for the old q_proj/down_proj shape matrix is not fully reproducible.

Latest bounded recovery:

`hrl/c16-e1-qwen25-shape-lowbit-109-v1@5563c7bc9320f6699f351307b2895093d0658d97`

Final status:

`HISTORICAL_MEASUREMENT_INPUT_AUTHORITY_NOT_REPRODUCIBLE`

Facts:

- historical q_proj M1/M256 output SHAs can be reproduced from the known V8 exact-stream path;
- historical down_proj M1/M256 output SHAs cannot be reproduced from the same accepted provenance path;
- node164 targeted search found no missing durable RAW activation authority;
- no V8/V9/AWQ state was promoted as a replacement;
- RAW_FP16 bridge was not run.

Therefore:

> The old eight-point matrix is preserved as historical evidence, but it is no longer the primary controlled E1 authority.

The next E1 stage creates a new, explicit, durable common-input baseline from scratch.

---

## New scientific comparison

The primary controlled comparison becomes:

`semantic operator × M shape × implementation`

with:

- semantic operator: `q_proj`, `down_proj`, `up_proj`
- M: 1, 256
- implementation:
  - `RAW_BF16`
  - `RAW_FP16`
  - `AWQ_FP16_INPUT`

Primary model family:

`Qwen2.5-7B-Instruct`

RAW accepted deployment:

- model: `Qwen/Qwen2.5-7B-Instruct`
- revision: `a09a35458c702b33eeacc393d103063234e8bc28`
- model root historically used on node109:
  `/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28`

AWQ accepted deployment:

- existing C16/AWQ asset and runtime from V7/V10 authorities;
- do not change package/runtime/backend.

S2_TEXT common token authority:

`0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`

---

## Canonical input authority

For each role independently:

1. Run one reproducible RAW Layer0 natural S2_TEXT prefill M2048 execution.
2. Live-hook the exact semantic module input:
   - `model.layers.0.self_attn.q_proj`
   - `model.layers.0.mlp.down_proj`
   - `model.layers.0.mlp.up_proj`
3. Freeze the full M2048 BF16 tensor.
4. Define:
   - M256 = exact first 256 rows;
   - M1 = exact first row.
5. Persist tensor bytes and SHA256.

These become the new authority:

`C16_E1_CANONICAL_RAW_ACTIVATION_V1`

No historical E1 output SHA is required for this new authority.

The new authority must instead be validated by:
- exact model/token/source identity;
- same-run module capture;
- same-process/direct module replay;
- repeated regeneration producing the same activation SHA under the frozen source/runtime.

---

## Dtype bridge contract

The BF16 canonical activation is the semantic source.

Create a FP16 cast for every shape.

Require:
- all values finite;
- BF16 -> FP16 -> BF16 round-trip is bitwise equal for the activation tensor.

For RAW_FP16 weights:
- cast the exact RAW dense module weights/bias once to FP16;
- require finite values;
- where applicable verify BF16 -> FP16 -> BF16 round-trip equality.

Then:

- `RAW_BF16` consumes canonical BF16 activation;
- `RAW_FP16` consumes canonical FP16 activation;
- `AWQ_FP16_INPUT` consumes the **same FP16 activation bytes** as RAW_FP16.

This yields a much cleaner comparison than the historical natural-state pair.

It still remains an **implementation-level comparison**:
AWQ and RAW_FP16 have different weight representation/kernel implementation.

---

## Historical evidence retained, not erased

Historical accepted artifacts remain useful for context:

- C16 V10 RAW/AWQ matched semantic-module deployment comparison:
  `57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`
- AWMA E1 historical eight-point matrix:
  `56096d32bd5cd783286e1b5e5e612b6019f926d0`

They must be labeled:

`HISTORICAL_DEPLOYMENT_MEASUREMENT_PROVENANCE_LIMITED`

and must not be mixed numerically into the new clean-baseline primary table as if they shared one input authority.

---

## Node roles

### node109

Owns:
- canonical activation creation;
- all GPU execution;
- clean timing matrix;
- operator holdout;
- optional CODE holdout;
- bounded implementation-transition diagnostic;
- conditional NCU deep diagnostic.

All foreseeable node109 work for this E1 stage is one Goal. Do not stop merely to ask whether to continue from lightweight timing to the pre-authorized bounded NCU stage.

### 174-new

Runs in parallel:
- independent authority/design audit;
- node164 CODE-input/asset discovery;
- build the clean-baseline consumer/comparator;
- pre-register analysis and selection logic;
- if 109 results are already available, consume and independently verify them;
- otherwise stop at `READY_FOR_109_CLEAN_BASELINE`.

No GPU work on 174-new.

---

## Current claim boundary

Allowed after clean baseline if supported:

- timing/path behavior depends on operator, M shape, dtype, and deployed low-bit implementation;
- a same-FP16-input RAW_FP16 vs AWQ comparison exposes deployment implementation differences more cleanly than the old natural-state comparison.

Still not automatically allowed:

- quantization alone causes all differences;
- cache/TLB causes timing differences;
- end-to-end model speedup follows;
- behavior generalizes to all low-bit models.

