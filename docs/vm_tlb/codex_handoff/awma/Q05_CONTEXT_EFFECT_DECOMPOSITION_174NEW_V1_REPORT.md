# AWMA Q05 Context-Effect Decomposition 174-new V1

Status: `AWMA_Q05_CONTEXT_EFFECT_DECOMPOSITION_174NEW_V1_COMPLETE_WITH_SCOPE`

A target-only ideal-translation (I0) counterfactual was implemented in a separate diagnostic runtime. Every predecessor remains natural F0/R0; only the exact Q05 launch bypasses modeled translation while preserving identity-compatible lower-memory addresses. No TLB/PTW/cache mechanism parameter was changed.

## Results

| Context | R0 cycles | Q05-I0 cycles | I0 delta | Sensitivity |
|---|---:|---:|---:|---:|
| Formal isolated member34 | 864552 | 670682 | -193870 | -22.42% |
| P2 | 848511 | 701244 | -147267 | -17.36% |
| P8 | 835145 | 664241 | -170904 | -20.46% |
| P34 | 871835 | 674121 | -197714 | -22.68% |

P34 retains a 197,714-cycle target-only translation sensitivity despite just 15 natural walks and 249 L2-TLB misses. Hence cold isolated replay inflates PTW/walk frequency, but does not eliminate the modeled total translation-path sensitivity under real context. The remaining P34 sensitivity cannot be assigned to a concrete mechanism from this study alone; lookup/service and other source-modeled translation-path work remain candidates only.

P8 and P34 I0 sensitivities are similar, while natural cycles differ substantially. P8 may be a future screening-prefix candidate, subject to scientific review; P34 remains the realism reference. Existing counter contrasts support `NON_TRANSLATION_CONTEXT_EFFECT_PRESENT`, but do not prove a single L2/DRAM cause.

P8 and P34 diagnostic-disabled controls exactly reproduce accepted natural metrics. The optional L2 target-boundary ablation was not safe under accepted source/F0 semantics and was not attempted. Raw logs and engineering receipts remain durable at `/root/share/mnt164/huangrulin/awma_q05_context_effect_decomposition_v1/`.

STOP: no mechanism experiment follows this stage.
