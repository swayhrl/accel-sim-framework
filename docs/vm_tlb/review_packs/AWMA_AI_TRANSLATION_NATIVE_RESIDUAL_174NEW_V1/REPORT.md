# AWMA_AI_TRANSLATION_NATIVE_RESIDUAL_174NEW_V1

Final status: **NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1**

All four preregistered Native targets are simulator-qualified. L2 was unlocked
through deterministic, byte-identical consumer normalization of exact
`LDC.U8 width=0` implicit constant-load records; no address or instruction was
invented.

L1 and M1 are the same implementation at an exact 8x CTA scale. Per CTA they
match at 67,464 simulated instructions, 514 dynamic memory instructions,
16,388 active-lane refs and 770 logical translation requests. Their local page
behavior is therefore the same; aggregate working set differs.

B1 changes cycles by +13.955% on L1 and +19.793% on M1, classifying both as
`ACCESS_PATH_MODEL_SENSITIVE_ONLY`. L2 changes by -0.109% and M2 remains a tiny
B0-only control; both are `NO_MATERIAL_TRANSLATION_RESIDUAL`.

On L1/M1, B1 reduces translation-not-ready events while increasing L1D
reservation-failure attempts. The net cycle gain is therefore a path/schedule
response, not an additive translation-time fraction or a free real-hardware
speedup. Both arms' service and cache outcomes are retained in the matrix.

No target has MSHR/PWQ-full pressure, no walker/capacity diagnostic is run, and
no differentiated residual/problem card/prototype exists.
