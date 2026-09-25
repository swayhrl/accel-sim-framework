# Passive last translation result forwarding V2 contract

Candidate: `PASSIVE_LAST_TRANSLATION_RESULT_FORWARDING`

Runtime selector: `GPGPUSIM_AWMA_TRANSLATION_CANDIDATE=passive_last_result`.
Default and all other candidates are unchanged.

## State and identity

- Exactly one entry per live dynamic memory instruction/accessq.
- Entry fields: ASID, VPN, page size, translation generation,
  read/write/atomic access class, resolved PPN, and original translation source.
- State is keyed by `(shader id, dynamic warp-instruction uid)` and is erased
  when that instruction's accessq becomes empty.
- No cross-instruction, warp, CTA, kernel, or process persistence.

## Operation

- V2 performs no resident-access prelaunch and creates no owner/member state.
- At the existing head translation decision point, an exact entry match
  computes PA from stored PPN plus the current page offset, applies translation
  exactly once, and does not call the translation controller.
- On a miss, the exact head follows the frozen controller path. Only after its
  natural READY result is legally applied does it install/overwrite the entry.
- Generation or access mismatch is always a miss. No unsupported permission
  dimension is invented.
- Forward hits never update the entry; only paid natural completions do.

## Finite timing/resource semantics

- Capacity is fixed at one; there is no capacity, fanout, or threshold knob.
- The implementation models a same-cycle one-entry compare/forward datapath at
  the already-existing head decision point. It consumes no translation port
  and adds no controller request.
- This is not a free lookup claim. Independent qualification must include
  compare/mux timing and PPA sensitivity; a later physical design may need a
  fixed pipeline stage, but this development stage does not tune latency.
- Storage is bounded by the number of live memory instructions, one entry each.

## Prohibitions

No proactive lookup, owner speculation, waiting, future information, free
cancellation, second-TLB semantics, or sharing beyond the current instruction.
