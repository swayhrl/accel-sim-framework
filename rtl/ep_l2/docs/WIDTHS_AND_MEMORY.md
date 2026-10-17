# Widths, state and excluded memories

Full cost always Tags1024, payload1168, WAD128, banks4×292, line1024bits,
sector256bits. Payload146KiB =1,196,032bits, equally partitioned SRAM capacity
for all modes. No technology macro area/delay is assumed to be zero.

- Payload ID11bits (max1167), row9bits (max291), Tag ID10bits, WAD index7bits.
- 64-bit native line addresses retained conservatively. Upstream alignment is
  part of the boundary; cost does not quietly narrow to an unproved GPU PA.
- Payload generation32bits, preserving source unsigned width. Release and
  reserve each advance it; clean reuse advances by2. Saturating admission
  guards refuse reuse before modulo wrap. This is **not** a proof that32bits
  suffice for unbounded GPU lifetime. A quiescent reset requires all external
  events drained; reset is not an ABA repair for outstanding old events.
- WAD completion uses its own32-bit allocation generation plus7-bit index:
  payload may already be reused before set_done. A stale old WAD token cannot
  erase a new live entry. WAD generation at saturation is retired, not wrapped.
  These explicit hardware token fields are not C++ pointer sizes.
- Pin count6bits (0..32), total10bits (0..512) share read-snapshot and external
  MSHR-descriptor accounting. Full MSHR content/merging remains external.
- Payload role3bits; Tag owner10bits plus4-bit ready/pending/dirty-sector state.
  Per-byte dirty state is reused from traditional Tag logic; its external
  cost is unknown, not implicitly zero. Byte-protect AND/write paths and
  captured WB128-bit masks are inside this RTL.
- Copy/read latch1024bits, pending request data1024bits, read response
  snapshot1024bits and WB output snapshot1024bits are actual synthesized
  standard-cell state/data paths. These are NOT SRAM payload storage.
  Unified's common latch is active in WB readout; static also copies through it.

The control metadata tables are actually mapped into standard cells in this
first flow, including their mux/write decode. No metadata SRAM saving is
assumed. Functional SRAM wrapper alone uses a memory array, hidden by an
explicit blackbox under SYNTHESIS. Controller top excludes that blackbox at
well-defined port cuts; real4-bank macro binding remains future work. Exact
metadata cell cost can motivate a later real metadata-memory implementation,
but its ports/latency must then be accounted and SIM_RTL_TIMING_GAP updated.
