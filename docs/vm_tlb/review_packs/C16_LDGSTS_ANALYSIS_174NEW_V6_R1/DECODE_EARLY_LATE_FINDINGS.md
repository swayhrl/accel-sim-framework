# Decode Early vs Late

Observed facts: both occurrences have the same frozen static-map SHA, 33 executed static indices, and 33/51 executed/zero partition. Decoded active-lane events are 460208 (Early) and 466928 (Late), delta 6720.

Supported interpretation: this is an independently decoded LDGSTS GLOBAL-SOURCE read-path difference at set level; it is not producer callback accounting.

Unsupported hypotheses: no cross-replay absolute-VA comparison, no whole-kernel footprint, no temporal/reuse claim, and no KV-growth causal claim without a common lossless semantic object identity.
