# Candidate repair contract — gated, not implemented in the consumer

The recovered historical algorithm uses **execution-lane distance**. For an accepted mode1 record, `A[lane] = base + (lane - first(E))*stride` modulo2^64, for lanes in the printed predicate intersection `P`. Its encoder required contiguous `E` with at least two lanes. `first(E)` need not equal `first(P)`. Advancing once per printed active lane is contradicted by the source when P has internal holes and stride is nonzero. A decoder that only skips predicate holes still does not fix a missing base anchor.

For `P=fffcfffc/base128/stride4`, active lanes2/15/18/31 illustrate the difference:

| Interpretation | Addresses |
|---|---|
| Frozen consumer | 128,180,0,0 |
| Advance once per printed active lane | 128,180,184,236 |
| Historical source, E starts at lane2 | 128,180,192,244 |
| Historical source, E starts at lane0 | 136,188,200,252 |

The last two are source-consistent per-record candidates. No full-input choice is approved. A matched binary/control-flow proof could establish E for some or all PCs; an inference from legal-looking addresses or improved bank timing cannot.

If the exact input interpretation is later qualified, prefer an **offline, member-whitelisted, fail-closed normalizer** that emits explicit mode0 active-address lists into a new derived input directory. Required inputs are the exact original member SHA, reviewed producer-family binding, and a per-record execution-mask/address receipt with independent evidence and line identity. Refuse missing/ambiguous evidence, noncontiguous mode1 E, invalid P subset E, wrong address-token count, nonrepresentable stride or mismatching source hash. Do not infer E from the printed mask.

For mode0, map the serialized list over the proven E lanes first, then retain P lanes. In this fixed member all3330 excess vectors have32 words, so full-E lane association follows **conditionally on the historical-family binding**. Leave zero-predicate records inert and preserve unrelated records exactly. No mode2 or other-format semantic change follows from this finding. Preserve the source opcode and its frozen width (`LDS.U` and `STS` are4 bytes).

Tests must compare against independently recorded raw addresses or a matched executable/capture proof, including counterexamples in CPU_TEST_RESULTS. Encoder/decoder round-trip alone is insufficient. The diagnostic tools in this branch do not emit a normalized input and cannot launch or release a row.

Impact if later implemented: Framework gains an offline tool and a derived input identity; Core protocol/resources need no change; existing runtime binary can consume explicit mode0 through its original path if separately validated. Original trace and old results stay immutable. A new parser/binary, if chosen instead, requires a new binary identity and a new applicability audit. Neither approach can claim current all11 equivalence from the sparse-mode1 inventory alone.

Minimal scientific reexecution is comparison-specific: for the main B16 versus IO/OO claim, register a new matched B16/IO/OO triplet after input review. Add TC80, TRAD96, IO128, WAIT128 or the modern baseline only for claims that actually use those rows. Old historical runs need preservation and disclosure, not wholesale replay. A owns admission and pairs; this helper authorizes no rerun.
