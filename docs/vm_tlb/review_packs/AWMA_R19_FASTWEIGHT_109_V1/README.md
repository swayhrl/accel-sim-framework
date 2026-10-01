# AWMA R19 fast-weight / TTT boundary on node109

Stage: `AWMA_R19_FASTWEIGHT_109_V1`

Final decision: `R19_FASTWEIGHT_STRONG_SOFTWARE_SUFFICIENT`

## Outcome

A real trained checkpoint was found and admitted only as a
`PUBLIC_REPRODUCTION_ARTIFACT`: `hungngo04/gemma-3-1b-it-ttt-tinystories-500k`
at Hub revision `c4ec10a9e061c64c7db5fd6277b3fa545292a49f`. It is not an official
In-Place-TTT paper checkpoint. The artifact contains trained BF16 weights,
custom model/config code, and five nonzero `ttt_conv`/`ttt_proj` pairs. Its
training provenance is an adapter-only Gemma-3-1B reproduction on 500,000
TinyStories samples, not the official continual-pretraining recipe.

The real input is a deterministic public HELMET-style Banking77 prompt built by
the reproduction harness from `PolyAI-LDN/task-specific-datasets` at
`57ec275d8078af65b7731c2a98be812d844a6d6b`, seed 1337. The fixed measurement
uses its natural first 256 tokens, exactly two artifact chunks (`ttt_chunk=128`).

The semantic canary passed on adapted layers `[0, 6, 12, 18, 24]`:

- every prompt-derived fast-weight delta was nonzero;
- the second chunk consumed `W_down + eta * delta`, and differed from base-only output;
- the five-layer ephemeral fast-weight state was 79,626,240 bytes;
- no model parameter changed across update/consume;
- an identical reset/repeat produced bitwise-identical final logits.

## Paired timing

All numbers are aggregate median/MAD over 15 formal samples: three groups,
two warmups plus five samples per arm per group, with alternating arm order.

| Arm | Median (ms) | MAD (ms) |
|---|---:|---:|
| Released batched five-layer path | 2.079488 | 0.007456 |
| Equivalent two-chunk PyTorch closed form | 1.592320 | 0.021472 |
| Update only, five layers | 1.192192 | 0.006912 |
| First dependent consumer, updated state ready | 0.237568 | 0.002205 |
| Base/no-write consumer diagnostic | 0.245760 | 0.002048 |

The bounded software reorganization is 23.43% faster than the released
`cat+cumsum` organization while preserving the same two-chunk math. It uses
ordinary PyTorch contractions: base consumes chunk 0 and `W_down + eta*delta`
consumes chunk 1. The updated-state consumer is not slower than the base
consumer (0.237568 ms versus 0.245760 ms). The remaining update cost is the
method's dense gate/up, depthwise Conv1D, target projection and outer-product
contraction, not a separable state-read/lifetime residual.

Therefore the observed material opportunity is software organization, and the
current evidence does not justify a fast-weight hardware mechanism.

## Scope and caveats

- One third-party reproduction artifact, one real public prompt prefix, one
  RTX4080, and one fixed shape only.
- This is a local update-to-first-consumer boundary, not end-to-end quality or
  throughput evidence.
- The Hub model code requires Transformers 5.6.2 APIs although its saved config
  records 4.57.3. A compatibility-only patch removes an invalid `@strict`
  decorator; it does not change model math or tensors. The patch is included.
- No training, random fast-weight proxy, model/shape sweep, 174 simulation,
  NSYS, NCU, NVBit, or SASS trace was run.

## Contents

- `FINAL_DECISION.md` — contract decision and claim boundary.
- `SOURCE_CHECKPOINT_INPUT_AUTHORITY.md` — bounded authority audit.
- `SOURCE_RECEIPT.json`, `INPUT_RECEIPT.json`, `RUN_RECEIPT.json` — exact receipts.
- `ARTIFACT_AUTHORITY.tsv` — all inspected checkpoint candidates.
- `RESULT.json` — all formal samples and semantic metrics.
- `TRAINED_TTT_TENSOR_AUDIT.txt` — checkpoint tensor qualification.
- `CONFIG_STRICT_COMPAT.patch` — compatibility-only source patch.
- `ENVIRONMENT.txt`, `GPU_LOCK.txt` — environment and lock receipts.
- `RAW_DATA_INDEX.tsv`, `SHA256SUMS` — raw publication and pack hash closure.
