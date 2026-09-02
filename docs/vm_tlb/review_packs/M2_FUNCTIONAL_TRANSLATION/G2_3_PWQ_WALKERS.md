# G2-3 — finite PWQ and fixed-latency walkers

Status: `PASS`  
Core: `e579c40d907c201728331a1208c64bb18b869549`

M2 misses enter a finite PWQ; a finite walker pool completes them after a
configurable fixed latency using the existing MSHR fill/release path.
`active_walkers <= walkers` is asserted each cycle. PWQ wait and walker
service cycles are separated.

`vm_m2_g2_3_test PASS` checks one walker, latency-three timing, no early
completion, two starts/two completions at quiescence, and PWQ-full
backpressure. Existing G2-1/G2-2 tests and the standard build passed.
