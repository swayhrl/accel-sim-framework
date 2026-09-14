# Trace scope audit

All six raw files are formally admitted selected-target captures from Recovery-V2:
`meta-llama/Llama-3.2-1B` revision
`4e20de362430cd3b72f300e6b0f18e50e7166e08`, C16 `S0/B1/T128/Decode4`,
RTX3090, CUDA 12.4, PyTorch `2.5.1+cu124`, and NVBit 1.7.5.

The selected target is deliberately narrow:

- Prefill: `indexSelectLargeIndex`, NVBit static range `[101,102)`, offset
  `0x650`, `LDG.E.U16`.
- Decode2/3/4: `indexSelectSmallIndex`, NVBit static range `[17,18)`, offset
  `0x110`, `LDG.E`.

The old candidate numbers 34 and 348 are not reused. The full model, other
memory instructions, other kernels, physical addresses, hardware page sizes,
TLB misses, and cache behavior are outside this trace scope.

The raw lines use `RAW_CTA`: CTA coordinates and warp prefix the PC. The H
parser retains the active mask, derives each active lane's VA, preserves width,
access kind, explicit GLOBAL memory space, kernel header, selected static
identity (from the commit-bound target JSON), and `COMPLETE` terminal state.
No separate predicate field is serialized beyond the active mask. Analysis is
`SET_ONLY`; source-file record order is not global execution or L2 order.

`UNKNOWN_RUNTIME` remains the object attribution because this publication does
not provide the required direct runtime object-map snapshot/cutoff. That does
not alter formal raw admission or selected-target structural metrics.
