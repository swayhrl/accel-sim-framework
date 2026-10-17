# State/memory accounting: charged, constant, external and verification-only

Full cost remains1024 Tags/1168 physical lines/128 WAD/GEN32/4x292/P1. Use
actual per-module Liberty sums, not a count of source declarations or C++ bytes.

- Used payload metadata words retain ALL32 generation FF, pins/ready/pending/
  dirty state and live role state. Static resident has51 FF/word after proven
  owner/role constants; WB-only staging has34 FF; Unified has63 FF/word.
  Counts are1024 resident+16/64 WB in B/S,1168 Unified. Static bypass metadata
  is constant in this finite WB-only mechanism; its physical data remains.
- Unified Tag-map is1024x11 real FF. B/S Tag-map/owner/upper role bits and one
  common captured resident-handle upper bit are redundancies removed by proof:
  exactly23553 FF per static mode. GEN width was not shortened; U FF unchanged.
- WAD allocation generation is32 bits per128 entries and remains actual state,
  independently qualifying set_done after a data slot is reused. WAD64-bit
  addresses,128-bit byte masks, sent/live flags, FIFO and dynamic PID bits are
  charged. Constant bits of fixed static staging PIDs are ordinary documented
  mode pruning; full external address/identity interfaces remain.
- Four1024-bit data holding registers (request/copy/response/WB) and their real
  mux/byte-enable paths remain charged standard cells. Reset repeaters are
  actual2xINV gates, fully charged, no extra FF/cycle. Prefix arithmetic is
  real combinational logic, not an assumed free generation operation.

One source field needs explicit distinction: `wad_payload_gen` is read only
by the !SYNTHESIS invariant assertion at WB read grant. It is optimized out of
hardware in BOTH R1 and R2, not silently charged as a functional32-bit table.
The internal FIFO entry owns an immutable WB-role payload until its read has
completed and the held WB snapshot is accepted by lower. Only lower_accept
frees that local slot. set_done clears only its WAD entry; it never touches a
possibly reused payload. Thus no functional external operation consumes the
historical duplicate payload generation after reuse. Physical payload GEN32
and WAD ticket GEN32 remain and are checked on their actual late-event paths.
Changing this exclusive-ownership/FIFO contract requires requalification and
possibly functional duplicate-generation checks; an assertion is not that new
hardware. Debug-only counters/testbench or symbolic-version integers are not
represented as free implemented data/state.

Four292x1024 payload SRAM boundaries total146KiB. Their area/delay is UNKNOWN,
never default-DFF area or zero. Native full-address Tag/LRU/MSHR/dirty-byte
tracking/NoC/lower queues remain external and UNKNOWN. In particular the
128-bit protect/victim byte-mask interfaces require a correct external source;
this pack does not assert that an existing native cache supplies those masks
at zero hardware cost. Real macro adapters/ports/latency and that external
implementation must be costed before whole-slice or net benefit claims.

Formal scope is explicit: changed word arithmetic, selector helpers, reset
network and Tag-map mask have their attached proofs; global protocol and
physical correctness are not inferred from those alone. Actual full-size
functional fixtures supply their separate finite qualification. No whole-GPU
numeric/atomic/RO/TVD/post-map or physical closure claim is made.
