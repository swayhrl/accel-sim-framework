# Data/control/port comparison and missing hardware proof

| Structure | Additional raw data/SM |64SM|Status |
|---|---:|---:|---|
| Parent AC:2x80KiB banks |163840B|10485760B|unchanged production reference |
| Proposed AC2:2x4KiB banks |8192B|524288B|test-local bound only; production STOP |
| One drained serial owner with512 sectors |at least16384B|not a campaign size|source-API CPU witness; exceeds proposed total by8192B |
| One640-line all-sector owner |81920B|not a campaign size|accepted structural upper bound; manual fullpool CPU stress |

Keeping two4KiB banks and adding a separate general80KiB serial fallback would
cost90112B/SM (88KiB), not8KiB. Reusing the small banks as part of a general80KiB
serial buffer still needs73728B (72KiB) additional storage and reviewed bank
routing/control. These are cost alternatives, not approved implementations or
proved minimum RTL designs. For a512-sector source-domain owner, the raw-retention
lower bound alone is16KiB; a257-sector owner already exceeds8KiB by32B. A true
compact per-lane/warp-output approach may need less raw storage, but needs a new
byte-extraction, output-size and assembly ownership contract. No ISA bound or
value-correct assembly proof is supplied here.

Minimal logical stage bookkeeping estimate (excluding diagnostics and existing
PIB descriptors): two64-bit UIDs, two valid bits, one bank role bit and two
collected-count fields. Parent counts0..2560 need12bits each:155bits. Compact
counts0..128 need8bits each:147bits. This omits exact-demand accumulation
(12bits for0..2560), cursors/byte routing, fallback ownership, arbitration and
telemetry, ECC/alignment/implementation overhead. It is **not total control area**.
Software type sizes are not synthesized widths. A fallback control estimate is
incomplete because no feasible fallback state machine has been approved.

The original shared4x32B/cycle collection quota and1-instruction/cycle retire
quota are preserved. Raw-data banks need bounded collection writes and WB reads;
role swaps avoid bulk copies. An instruction retirement rate does not prove a
physical all-sector read/RFU routing bandwidth or clock feasibility. No new port
is free. No RTL, SRAM macro, synthesis, PPA, frequency, loaded values, native/GPU
execution or application timing result exists. No area-fair small-cache claim or
paper-final preference can be inferred from the requested8192B data capacity.
