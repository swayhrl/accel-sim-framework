# Generation provenance audit

Status: `POST_HOC_DIAGNOSTIC_ONLY`

## Evidence boundary

The accepted V34 commit `ab26365dc663268b0799818db6687ed466e8c925` contains the 18-file review pack but no producer runner/source file. Its commit delta contains no `util/` or Python runner. The exact 32-step generation command, loop, and cache transitions are not archived in the accepted commit. This negative finding prevents reconstruction by assumption.

The V34 specification requires `S2_TEXT = B1/T2048/D32` and says to execute exact native S2 with frozen IDs. The receipts establish:

- `S2_STATE_RECEIPT.json`: 32 decode steps, layer 1, `no_synthetic_state=true`, native S2 status PASS;
- `NATURAL_TOP8_ROUTING.json`: one 32-record array with unique consecutive steps 1–32, natural routing, per-step top-8/weights/router-input SHA/router-logits SHA/next token;
- `S2_INPUT_AUTHORITY.json`: 2,048 frozen prompt IDs, no retokenization after freeze;
- `ASSET_RUNTIME_RECEIPT.json` and `RUNTIME_CAPACITY_RECEIPT.json`: a hash-closed model replica and native BF16 runtime family;
- `MOE_RUNTIME_DATAFLOW.json`: observed per-expert native path, but not the generation loop.

The accepted V40 descendant's `olmoe_v40_marked_replay.py` is a later single-module replay: it loads `expert58_d32_input.pt` and calls only `experts[58].down_proj(value)`. It did not generate V34's 32 routing records and cannot fill the missing generation semantics.

## Question-by-question audit

| Question | Finding | Evidence / limitation |
|---|---|---|
| One continuous autoregressive generation? | `UNRESOLVED` | Required scenario and consecutive records are consistent with one run, but the actual runner/session receipt is absent. |
| Per-step model call or rematerialization? | `UNRESOLVED` | Runtime/model residency is recorded; per-step call/materialization behavior is not. |
| KV cache continuous? | `UNRESOLVED` | No cache object identity, length progression, or runner code is archived. |
| State reset between steps? | `UNRESOLVED` | No reset log or loop source exists in accepted authority. |
| Cyclic input or fixed-token injection? | `UNRESOLVED` | No input-token-per-step field or runner code. The next-token cycle is output association, not proof of injection. |
| Sampling vs greedy? | `UNRESOLVED` | No `do_sample`, argmax, temperature, or generation-config receipt. |
| Seed? | `UNRESOLVED` | No generation seed in V34 receipts. The audit shuffle seed is unrelated. |
| EOS handling? | `UNRESOLVED` | EOS ID/check/ignore behavior is not recorded. |
| `max_new_tokens`? | `EFFECTIVE_32_STEPS_ONLY` | Exactly 32 steps are recorded; the runner parameter and early-stop policy are absent. |
| Stopping criteria? | `UNRESOLVED` | No runner/config evidence. |
| Hook perturbation? | `UNRESOLVED` | Router values are recorded and state is labeled non-synthetic, but hook source and perturbation validation are absent. |
| One run or stitched states? | `CONSISTENT_WITH_SINGLE_RUN_NOT_PROVEN` | One artifact has consecutive steps 1–32, but lacks a run ID, timestamps, command, and cache/session binding per record. |

## Period-11 origin assessment

At lag 11, `19` of 21 pairs share the same recorded next token, while router-input SHA equality is `0` and router-logits SHA equality is `0`. Thus this is not exact hidden/router-state replay. The strong routing-set repetition is associated with output-token repetition, but the missing runner prevents deciding whether the token cycle arose from genuine autoregressive content behavior or capture/replay methodology.

Origin classification: `POSTHOC_PERIOD11_ORIGIN_UNRESOLVED`.
