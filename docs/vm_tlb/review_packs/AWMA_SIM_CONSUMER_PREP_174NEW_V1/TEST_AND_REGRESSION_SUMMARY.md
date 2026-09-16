# Test and regression summary

The parser driver compiled against the official repository parser with G++
11.4.0. `python3 -m unittest -v
util.vm_tlb.awma.simulation.test_simulation_foundation` passed 16 tests,
including all required negative gates, deterministic identity/catalog behavior,
telemetry normalization, five runtime status classes, and an end-to-end wrapper
smoke using a formally admitted fixture.

A real historical recovered trace with SHA256 `ebe2ca8b...2026` passed `xz -t`
and the official-parser-linked driver: one thread block, 84 instructions,
`TRACEG_GRAMMAR_PASS`. It is only a parser/admission regression fixture.

JSON syntax, Python bytecode compilation, executable modes, accepted source and
binary hashes, deterministic baseline identity, Schema member closure, old
baseline review-pack closure, and this review-pack closure are checked during
final closeout. C12 was not rerun.
