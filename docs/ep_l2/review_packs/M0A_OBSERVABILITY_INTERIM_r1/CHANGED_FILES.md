# Source diff summary

Core candidate delta from D512 parent: 221 insertions / 3 deletions in four
files: `gpu-cache.h`, `gpu-sim.cc`, `l2cache.h`, and `l2cache.cc`. It adds the
opt-in M0a configuration bit and the separate `EPL2M0AV1` accumulator/parser
stream; it does not alter the admission predicate.

Framework candidate delta: M0a ON/OFF config overlays, a fail-closed
`parse_epl2_m0a.py`, isolated runner, analyzer, and parser unit tests.

No Unified, RO, TVD, M0b, borrowing, or headroom implementation is included.
