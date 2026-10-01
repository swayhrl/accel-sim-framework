# Stage A dense-first scope revision

This is a CPU-only revision of the proposed measurement campaign, not an execution authorization or a new performance result. It preserves the design at `5f0335b5f991890348e60e1f23a546f393f86d8b` and the asset/input receipts at `c3f625e46adb8d5c4082ded8b61858c710e1f4e9`; only the *current executable scope* is narrowed. Historical design and canary artifacts remain unchanged.

## Authority and decision

| Authority | Frozen observation used here |
|---|---|
| Runtime qualification `3f62f909a474e4c56695ffacf36ddcb5d7b5f147` | BF16 MP01–03 runtime-ready. AWQ MP05 failed V1 instrumentation neutrality, though Graph OFF/ON correctness passed. OLMoE MP06 failed correctness/backend-identity gate. The runtime canary contains no scientific latency result. |
| OLMoE diagnostic `8b677cfa541877f559614f7bf22a40dd11cebd56` | `OLMOE_GRAPH_MODE_EXPERT_SET_DIVERGENCE`: 1,599 order-only events, 616 expert-set substitutions, zero structure shifts; frozen logprob tolerance fails at D1, D4, D6, D23, D29. Original `CORRECTNESS_OR_BACKEND_IDENTITY_FAILED` remains permanent. Underlying numerical cause is unknown. |
| Observer V2 source `f63d39c8d90ced038445c264fa8242c524a1aa6f` | Source-qualified, not runtime-neutrality-qualified. Its AWQ-only requalification canary is a draft for separate approval; no V2 PASS exists in this authority. |

MP06 is removed from the present Stage A active set as `CAMPAIGN_QUESTION_NOT_EXECUTION_READY`. The Graph-ON strong path and Graph-OFF instrumentable path have not passed their pre-frozen semantic-equivalence gate. Neither treating Graph OFF as the strong baseline nor declaring Graph ON an accepted standalone replacement after seeing failure is legal. No OLMoE repair or new equivalence test is designed here. A future OLMoE campaign would require a *new, prospectively frozen identity*, outside this Stage A.

The current core is MP01 (Qwen BF16 prefill), MP02 (Qwen BF16 decode B1), and MP03 (Qwen BF16 decode B4). MP05 (Qwen AWQ decode B1) remains a representation control only if an independently authorized Observer V2 runtime canary returns PASS under the original neutrality and correctness rules. A FAIL drops MP05 without replacement. MP04, MP07, and MP08 are holdouts and do not run; MP06 does not run. No budget from MP06 is reassigned.

The active questions are DQ1 natural critical-path composition, DQ2 B1-to-B4 small-M behavior, DQ3 memory/service candidate localization, and DQ4a dense producer-consumer handoff. The original DQ4 expert-turnover portion is separated as DQ4b `DEFERRED_NOT_EXECUTION_READY`. No MoE locality, cache, or page claim can be made from this campaign. Translation remains `UNKNOWN` and inactive. DQ4a is problem discovery on the dense Qwen path, not a promoted mechanism.

The graph-mode roles and Tier0 tools are frozen in `RUNTIME_MODE_MEASUREMENT_CONTRACT.md`. Original STOP thresholds remain unchanged in `UPDATED_STOP_RULES.tsv`; narrowing the point set does not make a weaker effect material. The original 20-minute eight-point design budget is historical, not permission to spend 20 minutes on this subset. The proposed future Tier0 caps are at most 6 GPU-active minutes for MP01–03, or at most 9 minutes if MP05 qualifies. These are point-reservation ceilings and require a separate reviewed 109 execution contract.

This review pack concludes `STAGEA_DENSE_FIRST_SCOPE_READY_PENDING_AWQ`: the dense core has an eligible source/runtime basis for a future reviewed Tier0 contract, while MP05 awaits Observer V2 runtime qualification. No GPU work, holdout execution, profile, trace, simulator, or performance analysis was performed in this revision.
