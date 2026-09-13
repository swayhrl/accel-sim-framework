# NVBit 1.7.5 minimal capture qualification

Status: `NVBIT_RETRY570_NVBIT175_MINIMAL_CAPTURE_QUALIFIED_STOP_FOR_REVIEW`.

This is a tiny deterministic PyTorch `index_select` canary, never a model,
C target, performance result, or scientific capture. Both independent Q1
processes used the frozen Q0 kernel 6 full `indexSelectLargeIndex` function,
NVBit 1.7.5, EAGER loading, the original Lane G tracer, and the same output
checksum `8c62c08fcc833f223182df024f4ed698c8e3fc93daf8e259c14d35e8899e665c`. Q0 and both Q1 prewarms produced zero trace
files before the parent created `MEASUREMENT_ACTIVE`.

Run1/run2 each completed normally within the 30-second target cap and emitted
exactly one trace with 7360 records and
192 explicit LDG/STG/ATOM address rows. Their
trace SHA256s are `ef149f38d4a00867c7d5d33dbbf1c05647264053d090bab19087ec230f2b0b91` and `b465afd2b9f41376ddd84edadb432dd2750bcbabbb88606369c6e078be4f25b1`; bytes
are both 481651. The two payloads intentionally differ by
run-specific address/context data, while target identity, schema, record count,
and required header fields agree.

The tracer format has no record timestamp or global sequence field. This pack
therefore does not falsely claim per-record timestamp ordering. Window
cleanliness is instead proven by the parent-controlled protocol: zero traces
before arm, `LANE_G_RUNTIME_READY` before `CAPTURE_BEGIN`, one armed target,
then `CAPTURE_END`, normal exit, and post-run marker/process absence. The
trace parser verifies header/version, target identity, complete instruction
rows, address-bearing memory operations, final newline, and one-file binding.

All retained Q0/Q1 payloads were remote-SHA listed, copied locally, and
rehashed identically. Raw traces stay outside Git. Stop here for review: this
does not authorize Llama, Qwen, a full model, C frozen targets, performance
analysis, or any broader scientific capture.
