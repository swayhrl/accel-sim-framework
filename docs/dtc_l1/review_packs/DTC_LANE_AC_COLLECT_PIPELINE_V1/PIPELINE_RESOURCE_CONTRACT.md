# OPT-COLLECT bounded resource contract V1

Authorization is DTC_LANE_AC_COLLECT_WB_PIPELINE_174_V1, CPU-only on original174.
Base Core is exactly e32afdcf44be3374ff36d22568ed01a075459b6f, whose direct parent
is c0a5e2c31e407c57e3a4af3ce529c921e8059a05. Existing AA5/X2 evidence remains
frozen. No full/canary/native/GPU execution is authorized by this pack.

`-gpgpu_dtc_l1_collect_wb_pipeline` defaults to0. ON requires PAPER_OO (3),
finite service V1 (1), and the existing ordinary L1D. Other modes, finite0,
disabled L1D and the external-cache constructor fail closed. K1 remains an
independent option with its original scope/normal-export contract.

At most one collecting owner and one waiting-WB owner exist per LDST. Both
continue to occupy their original PIB entries. UID stage ownership never moves,
reduces or recreates physical Refs, waiter ownership or completion dependencies.
The original full-admission, frontend-ready and older-same-warp-PROXY_FENCE guards
are rechecked. A later independent warp can progress past a blocked candidate;
a younger instruction cannot collect across its older same-warp fence.

The collection stage runs after the unchanged LDST WB arbitration on its first
invocation per absolute core cycle, including when another WB client wins. It
uses the original `service_entry::collect` and original width4 sector quota.
The existing start-of-LDST `observe_ready` loop is unchanged. No collection in
the observed ready cycle, and WB requires **cycle > collect_done_cycle**. No
same-cycle completion forwarding is introduced. A successful old WB and a new
collection can use different banks in the same absolute cycle. Repeated LDST
microsteps cannot replenish ports. At most one pipeline RFU attempt per cycle
is made; a denied attempt retains the result and retries on a later cycle.
The existing retire quota remains the authority for at most one cacheable OR
sidecar retirement per cycle. The ordinary WB arbiter/priority update and RFU
implementation are unchanged.

A completed collector promotes only into an empty result slot. A collector may
keep collecting while the result waits for WB. Once it finishes behind a full
result slot it holds its bank; no third owner may collect. This backpressure
persists through WB denials. Collection completion releases no Ref. Successful
RFU WB alone enters READY/CLOSED ledger transitions, then the original frontend
retirement releases physical references. Sidecars own no result bank and only
retire their already-completed observation; they never repeat store/atomic/
bypass/fence architectural effects.

## Explicit data cost, not free PIB storage

This is the pre-existing simulator's timing/identity domain, without load-value
payload simulation. We conservatively charge two finite **raw-sector** data
banks, including unused bytes; we do not assume an unproved compact warp-output
packing or free storage in128 PIB descriptors. No host byte vector is pretending
to verify loaded values. The modeled data-storage charge is explicit even though
C++ represents it by bank ownership and bounded sector counts.

Let P be the configured physical-line pool (unchanged). Each bank has4P sectors,
32B/sector =128P bytes. Every fully admitted unique logical reference pins a
physical identity; no candidate can simultaneously own more than P distinct
physical allocations. Its requested sector masks contain at most4P sectors.
This source-structural bound also avoids assuming that all source instructions
have only32 addresses: scalar-thread multi-address/local splitting and other
source paths exist. Acquisition above the finite bank bound aborts loudly;
it cannot allocate extra storage, narrow masks or discard bytes.

At the fixed640-line pool, each bank is81,920B =80KiB, and the two banks cost
163,840B =160KiB **additional data capacity per SM**. For64SM this is10MiB of
additional data capacity. Existing80KiB physical data, logical Tags, PIB128,
Ref width, request width, all service quotas, clocks and lower cap stay unchanged.
This conservative upper-bound implementation is not an equal-area optimization.
It provides no SRAM/DC/port/frequency/area result, and may be an unattractive
hardware cost. Compact lane/output buffering would require a separately reviewed
byte-extraction/routing and output-size contract; it is not silently substituted.

The bank assigned to the collector retains exactly the sectors already read,
in the original PIB-reference order and ascending sector-bit order. A result
bank holds all requested sectors for its one instruction. For one warp/instruction,
collector bytes already saved =32*(total_sectors-sectors_left); WB bytes saved
=32*total_sectors. Each is bounded by81,920B at P=640. The4/8/16-sector
instruction fixtures correspond to128/256/512 raw data bytes, respectively.
We store the conservative raw-sector image, not an assumed fixed128B warp
output. Fanout/extraction into architectural destinations remains the original
functional-path/routing domain; a compact warp-output maximum and physical
bank-to-RFU implementation have not been proven here. Descriptor addresses,
sector masks and output register routing stay in the existing referenced PIB;
there is no new per-PIB payload array. With two unfinished/blocked owners, at
most2*4P sectors are retained. Transfer is a swap of the two banks' roles and
owner identifiers, not an instantaneous80KiB data copy. Data reads still use
4*32B/cycle. No new bank ports or bulk copy path is modeled.

Additional control comprises two valid bits, two owner UIDs, the bank-role bit,
per-bank collected-sector counts (12bits each at2560 sectors), capacity checking
and the fixed-width telemetry counters. Source C++ UID/count types are conservative
software representations, not synthesized hardware widths. Whole-warp result
mapping and loaded values remain outside CPU proof. We charge raw-sector capacity
rather than claim a smaller warp-output maximum without proving it.

K1 invalidation may remove the lookup mapping while either bank owner lives.
Original physical identity/generation and Ref protection remain authoritative.
The pipeline neither relooks up old data by logical Tag nor consumes/duplicates
returns. The existing source request/ordinary pending-commit telemetry is unchanged.
Atomic K1 zero-added simulated-cycle cost remains its pre-existing model assumption.
Additional host statistics output implies no GPU-cycle or hardware-area result.
