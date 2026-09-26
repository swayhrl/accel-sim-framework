# Semantic decision

`SEMANTIC_EQUIVALENCE_PASS`

For primary step16 and holdout steps8/24, both B8 and B32 preserve exact output shape/dtype, finite logits, exact greedy argmax token, exact top-8 token-ID set, and exact top1/top2 ordering. Different-element count and FP16 error metrics remain recorded but are not gates. This claim is limited to the frozen greedy-decode trajectory and does not cover general sampling.
