# Nearest-software capability delta

This is a bounded source audit, not a new literature survey or novelty claim.

| Capability | Online signal consumed | Dynamic legal-set support | Index/gather location | Dense/indexed dispatch exposed? |
|---|---|---|---|---|
| XGrammar 0.2.8 | CPU `int32` bitmask; `fill_next_token_bitmask` returns only a `need_apply` boolean | Arbitrary grammar masks for filtering logits; it does not skip LM-head weight rows | No indexed head; accepted A0 copies mask to GPU and applies it after dense projection | No |
| Kestrel `f61d3c7...`, `text.py` blob `50ac9a5...` | Caller-supplied optional `indices` tensor | Arbitrary supplied indices at the function boundary | `module.lm_head.weight[indices]` and bias gather immediately before linear projection; caller must create/transfer indices and remap outputs | Only an `indices is None` branch, not an online policy or union publisher |
| FlashSampling v2 / R81 A1-style fused selection | Hidden state plus dense tiled vocabulary, optional mask/bias | Masking is mathematically supported, but the fused path still traverses the dense vocabulary rather than consuming compact legal IDs | No legal-row gather; selection is fused into dense tiled LM-head work | No dense/direct-index dispatch policy |
| R81 A3 direct-index prototype | CPU bitmask/done state, then CPU legal IDs and identical-mask groups | Exact arbitrary legal IDs for the frozen B4 path | Per-group IDs and row metadata copied H2D; kernel loads original BF16 W at legal rows; candidate reduction returns global IDs | Arm is selected externally; no RULE_U01 implementation |

RULE_U01 would therefore be a small software policy over known dense and
direct-index primitives, not a new hardware mechanism. The unresolved part is
the exact pre-head union publication/reduction and its cost. Kestrel proves that
an indexed head primitive exists, but does not make legal-ID formation, H2D,
grouping, or dense/indexed dispatch free. FlashSampling covers fused dense
selection, not compact dynamic-row traversal. XGrammar supplies the mask, not
the required union statistic.

Pinned receipts:

- XGrammar wheel SHA256:
  `d6576539ade4b2404c38f606f4d04a1d6d22023fa03f9cab98bff894877696024`.
- Installed `matcher.py` SHA256:
  `02fe4d9507c7feb3c7498306d47be52751a332fb7499c375483768898eb46f01`.
- Kestrel source file SHA256:
  `eddcc579227a8dc6bc99e736987d48f0f682f686fd440047ceabe87651f156e1`.
