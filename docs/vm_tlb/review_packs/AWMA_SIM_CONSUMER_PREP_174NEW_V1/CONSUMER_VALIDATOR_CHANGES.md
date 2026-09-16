# Consumer validator changes

`simulation_foundation.py` now admits only a hash-closed
`SIM_COMPAT_CAPTURE_V1` bundle with an explicit complete terminal receipt,
zero drop/overflow, safe kernelslist commands, exact semantic encodings, a
nonempty required-control opcode contract, and a successful `xz -t` plus real
grammar parse of every listed trace.

The grammar driver links the repository's authoritative
`gpu-simulator/trace-parser/trace_parser.cc`. A strict structural pass also
checks headers, CTA/warp termination, instruction counts, opcode, memory
access/space/width semantics, active-mask address arity, and trailing tokens.

The formal `SIM_INPUT` catalog record and JSON Schema now use the same flat
identity fields. Its ID binds bundle/list/trace roots, terminal receipt,
workload and target, producer/tracer, runtime, launch, and address context.
C16WARP1/MREF is returned as `NOT_PROVEN_LOSSLESS` with no ID.
