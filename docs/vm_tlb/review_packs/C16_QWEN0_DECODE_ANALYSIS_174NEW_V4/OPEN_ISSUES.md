# Open issues and scoped discrepancies

- Producer `address_count_replay_diagnostic=33` for Early Heavy is the unique starting-VA count after a replay union. Independent active-mask decoding yields 65 active lane-address events (one zero address, thirty-two repeated zero addresses, and thirty-two nonzero addresses). The review pack keeps these as different metrics.
- All observed Decode addresses are outside their own same-process context ranges, so object attribution remains `UNKNOWN_RUNTIME` and early/late object-relative normalization is unsupported. No cross-process fallback map was used.
- The Flash function has 84 `LDGSTS...128` `GLOBAL_TO_SHARED` static rows outside the frozen 41-row direct-GLOBAL-MREF set. The accepted runs remain valid for direct `GLOBAL + MREF` scope, but do not cover every physical global-memory path.
- Bare `LDG.E`/`STG.E` accesses remain `WIDTH_UNKNOWN`; touched-range footprints are reported only for exact-width subsets.
