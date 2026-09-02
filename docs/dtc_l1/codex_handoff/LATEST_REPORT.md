# Latest Codex Report

Stage: `M4_COMPUTE_BRINGUP`

Status: **STOP — HARD FAILURE: PROXY-FENCE PTX FRONTEND UNREACHABLE**

Core M3 checkpoint: `90cb35d5c4f9511a2eacb9e0e809a2d9c74ecb2c`

Framework M3 implementation/parser checkpoint:
`800fc95fe2b502e30e76ce1cb6de050f6069178e`.

## M3 closeout status

Whole-line OO random-access retirement, line-level Ref Count, merge/wakeup,
active reclamation, O01–O13, IO-vs-OO causal HOL, and the 4x32B sector
extension S01–S09 have passed. Real modes 2/3/4 VecAdd self-checks and strict
provenance parsers are recorded in:

`implementation/M3_OO_SECTOR_EVIDENCE.md`.

M2 recovery evidence remains authoritative historical context in:

`implementation/M2_IO_RESPONSE_RECOVERY_EVIDENCE.md`.

## M4 partial progress and HARD stop

M4 source audit and its failure evidence are in
`implementation/M4_MEMORY_OP_SEMANTICS.md`. Store/Atomic/bypass lifecycle
observation was implemented without changing their source request/cache/ack
or atomic-side-effect paths. Core build/CTest passed; modes 2/3/4 VecAdd
passed with Store lifecycle closure; the available atomic-contention workload
passed with Atomic lifecycle closure.

However `src/cuda-sim/ptx.l` and `ptx.y` contain no `fence` opcode or
`FENCE_OP` mapping. The existing LD/ST proxy-fence path is therefore
unreachable from loaded PTX. A second source audit also found no static PTX
decode case and no producer of `set_proxy_fence()` or
`set_fence_proxy_kind()`; it is not a lexer-only omission. `membar` is a
distinct operation and a regular fence asserts unsupported. F01--F03 cannot
be run without adding parser, decode, and semantics work, which is outside the
authorized M4 scope. This is a reproducible M4 HARD failure.

External raw evidence (not committed):

- `/tmp/dtc-l1-r20/m4-fence-frontend-audit.log` SHA-256
  `d8fb91298affb8806380bc5a911ef50a37232ef7ca110a4557412330f3569839`;
- IO/OO/sector VecAdd logs: `002abddd…`, `5b4a4160…`, `8fb2e616…`;
- atomic-contention IO log: `c2350349…`.

No M4 review pack was created, M4 is not accepted, and M5 remains forbidden.
