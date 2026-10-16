# EP-L2 PPA ledger — raw storage bits, operations and unresolved physical costs

Scope: Lane 6, 2026-10-16. This ledger is a hardware field inventory, not a
C++ allocation estimate. `sizeof`, STL node size, simulator RSS and software
pointer width are not used as silicon area. No gate count, mm², power or Fmax
has been measured for this candidate.

## 1. Exact payload budget

| Configuration | Data slots/slice | Bits/slice | Bytes/slice | KiB/slice | MiB/64 slices | Organization |
|---|---:|---:|---:|---:|---:|---|
| OLD_D512_STATIC | 1152 | 1179648 | 147456 | 144 | 9 | 4×288 |
| B8_BANKED / U_WB8 | 1160 | 1187840 | 148480 | 145 | 9.0625 | 4×290 |
| B16_BANKED / U_WB16 | 1168 | 1196032 | 149504 | 146 | 9.125 | 4×292 |

Each slot is 128B=1024 raw data bits. C16 adds 2KiB/slice (128KiB/chip)
relative to OLD; C8 adds 1KiB/slice (64KiB/chip). The new primary and its
unified candidate have equal raw data bits. These numbers exclude ECC,
redundancy, SRAM periphery, metadata, wires, queue storage and banking costs.
They do not establish equal physical area or energy. Resident Tag capacity
remains 1024; 1168 slots do not mean 1168 cacheable resident lines.

## 2. Parameters and representation choices

| Symbol | Meaning / bound | Current treatment |
|---|---|---|
| N | Payload slots | 1168 primary, 1160 sensitivity |
| P | Payload ID width | ceil(log2 N)=11 for both |
| T, M, D, W | Resident tags, Line-MSHRs, descriptors, WAD | 1024, 128, 512, 128 |
| I_T, I_D, I_W | Index widths | 10, 9, 7; null/valid separately encoded |
| Q | Per-address requester bound | 32; explicit 0..32 count requires 6 bits |
| A | Byte address width | UNKNOWN for final RTL; illustrative scenario 48 |
| L | Full line key width | A−7 for 128B line; slice/hash-local reduction requires proof |
| G | Generation width | UNKNOWN until wraparound/late-reference proof |
| E | Epoch identity width | UNKNOWN; illustrative scenario 16, not a safety proof |
| R | Exclusive payload owner/role encoding | Illustrative 4 bits; final enum/state product to validate |
| K | Payload reader/pin count width | UNKNOWN; illustrative 6, range must include all concurrent references |
| T_RO | RO completion object capacity | Finite and bounded by descriptors/payload; scenario 128, not a chosen policy |
| J | Replacement/age width | UNKNOWN; illustrative 8 |
| Q_b | Per-Bank arbitration queue depth | UNKNOWN; illustrative 8 |
| O_b | Operation class width | UNKNOWN; illustrative 3 |
| X, O, S_R | Request identity bits, ordering bits, response metadata bits | UNKNOWN; not zero |

Generation G is safe only if no identifier wraps while a stale transaction,
pin, queue token or response can reference the old incarnation. If at most
R_reuses allocations can occur before every old reference is impossible,
then the implementation must prove 2^G > R_reuses (or an equivalent explicit
reuse quarantine/drain protocol). An average latency is not such a bound.
Neither illustrative G=8/16/32 nor a C++ unsigned proves safety. Tag and
transaction generations may require different widths; the shared-G scenario
below is a simplifying accounting assumption and may over/underestimate them.

## 3. Field-by-field account

All formulas are bits per slice. `COMMON` means present on both sides of an
equal-source comparison, not zero-cost. `CANDIDATE` is a proposed logical
representation whose actual implementation must be reconciled with Lane 1.

| Structure / classification | Raw-bit formula | Reuse / delta rule |
|---|---|---|
| Payload RAM / COMMON | N×1024 | Equal B_C/U_C; ECC/periphery separate |
| Resident Tag address/state / COMMON | T×(tag_key + valid + sector/replacement fields) | Existing Tag retained; tag_key depends on address mapping |
| Tag→payload pointer / CANDIDATE | T×P = 11264 = 1408B | Common if B_C already pointerized; otherwise explicit delta |
| Tag generation / CANDIDATE | T×G | Do not charge again if already included in a canonical handle |
| Payload canonical state / CANDIDATE | N×(R+4_valid+4_dirty+4_pending+K+G) | This is one proposed explicit packing; baseline equivalent state must be subtracted fieldwise, not assumed absent |
| Optional attached owner / CANDIDATE | N_att×(1+I_T+G) | Can be held only in RO objects; alternative, not automatically additive to per-payload state |
| Optional WAD owner backlink / CANDIDATE | N_back×(1+I_W) | Omit only if unique existing owner relation proves redundant |
| Request descriptor / COMMON | D×(X+mask+route+I_D+valid+response_state+owner_ref) | The pool remains 512. Requester IDs/routes are not software pointers |
| Descriptor next link / COMMON/DELTA | D×(I_D+1) = 5120 = 640B with independent valid | 9-bit pointer+valid; may share existing link representation, no second 512-entry pool |
| Chain endpoints / COMMON/RELOCATED | n_chain×(2I_D+2_valid+6_count) = n_chain×26 | M normal chains; RO chains either move with ownership or add finite T_RO state; don't count a moved chain twice |
| RO completion object / CANDIDATE | T_RO×[L+E+(P+G)+(1+I_T+G)+16_masks+26_chain+O+S_R] | Four sector masks are an explicit conservative candidate. Preserve ordering, atomic exclusions, cursor/pending response state; unknown O/S_R not zero |
| WAD full line key / COMMON | W×L plus existing lifecycle state | Existing 128 mandatory addresses; reuse does not permit increasing entry count silently |
| WAD/TVD pointer+gen / CANDIDATE | W×(P+G) | Pointer alone: 1408 bits=176B/slice=11KiB/chip |
| TVD incremental role/sector/age / CANDIDATE | W×(3_state+4_valid+4_dirty+J+1_pin) | 3 state bits is illustrative pending/inflight/clean etc.; real state enum must fit |
| TVD comparator / LOGIC | up to W×L key-bit comparisons per associative lookup | Not SRAM bits, not gate area. Banking/pipelining changes logic and latency |
| Allocator bitmap / CANDIDATE | N bits | Alternative free-list representation below, not both by default |
| Allocator free list / ALTERNATIVE | N×P + head/tail/count control | Quantify multi-allocation/update ports; do not add bitmap and list without real need |
| Global conservation counters / CANDIDATE | n_role×ceil(log2(N+1)) | Scenario n_role=10; some status telemetry may be simulation-only |
| Bank arbitration tokens / CANDIDATE | 4Q_b×(P+G+O_b+age_bits+token_valid) | Queue entries hold metadata only here; actual data buffers additionally charged |
| Bank scheduler combinational logic / LOGIC | fan-in, ready selection, fairness and mux topology | Requires RTL netlist/constraints, not a scalar bit-area conversion |
| Oracle map / OFFLINE + CONDITIONAL_HW | n_epoch,line×(L+E+eligibility+exclusion) before compression | Offline file/tool cost reported; hardware approximation is not free and not yet specified |
| Lower data buffers / COMMON or explicit DELTA | sum q_depth×carried_data_bits + control | Retain by scope; see §5 |

The RO row is not a complete numerical total: O and S_R remain unbound. Source
ordering maps and response lists cannot be deleted because the paper calls
the transaction MSHR-bypassed. If an RO object reuses a payload-side chain,
subtract the duplicated fields explicitly and identify the storage owner.

## 4. Concrete arithmetic scenarios, not implementation estimates

`PPA_STORAGE_SCENARIOS.csv` is generated for C=8/16 and G=8/16/32 using:
A=48, E=16, R=4, K=6, J=8, T_RO=128, Q_b=8, O_b=3, age_bits=8,
n_role=10. The scenario sets aside unknown requester/routing/ordering/response,
baseline Tag fields, ECC, oracle table and lower queues; its output field is
`illustrative_subtotal_bits_excluding_unknowns`, never `total_area` or
`hardware_overhead`. It charges the candidate RO chain in its completion row
and normal MSHR chains separately, while avoiding the optional per-payload
attached-owner duplication.

For C16/G16 specifically:

- Tag payload pointers: 11264 bits = 1408B/slice.
- Tag generation: 16384 bits = 2048B/slice.
- Explicit payload role/sector/pin/generation candidate: 44384 bits = 5548B/slice.
- WAD/TVD pointer+generation: 3456 bits = 432B/slice; additional state under
  the scenario is 2560 bits = 320B/slice.
- Descriptor next links+valid: 5120 bits = 640B/slice, a retained/common item.
- Normal chain head/tail/count+valid: 128×26 = 3328 bits = 416B/slice,
  retained/common. RO completion chains remain charged separately.

These fields can already be shared by a pointerized B16, so adding them all
to the candidate and subtracting none from baseline would overstate a delta;
assuming all metadata already exists would understate it. A final differential
ledger needs matched B16 and U_WB16 RTL field inventories.

## 5. Data movement, queues and ports

| Path | Data residency | Minimum service/accounting requirement |
|---|---|---|
| Static dirty resident→WBUF | Both source and destination live during copy | Source Bank read, destination Bank write, transfer buffering if not atomic; conflicts and pins explicit |
| Static WBUF→lower | WBUF then lower data carrier | Bank read plus lower enqueue; release only at successful transfer |
| Unified resident→WB_STAGED | Same payload, changed owner | Metadata transition; eventual data readout still consumes Bank service |
| Unified→lower | Source payload then lower carrier | Same real receive condition; pointer-only handoff keeps source pinned |
| Dirty TVD retention | Source slot stays after lower accept | Extra retained occupancy charged to pool, distinct from staging |
| TVD read / promote | Existing payload | Read service or atomic metadata visibility transfer; no free lookup/port |
| RO attached/detached return | Reserved payload landing | Fill write, response read(s), masks and final-reference pin |

Bank-matched B_C/U_C both have four Banks, one arbitrary line-sized operation
per Bank per cycle. A copy is not one free operation. The production interface
must declare whether a transfer uses two cycles, two distinct Banks, or a
pipeline register; accounting follows that interface, not the abstract diagram.
The exact candidate schedule remains pending Lane 1.

Queue storage scopes must not be conflated:

- L2→DRAM queue: 128 entries/slice. If every entry physically carries a full
  128B payload, raw capacity is 16KiB/slice, 1MiB/chip; if data is sector-sized
  or only present for writes, use actual width/valid packing and shared-data
  backing. A pointer alone is not evidence that these bytes disappeared.
- FR-FCFS scheduler: 128 entries/channel. It may hold commands/references;
  data ownership/backing must be declared before charging or excluding bytes.
- Internal DRAM ReturnQ: 192 entries/channel, separate scope from DRAM→L2
  boundary FIFOs. With a hypothetical full-line data carrier it is 24KiB/channel,
  768KiB/chip; this is a scenario, not the current hardware claim.
- Other boundary FIFOs, interconnect flits and copy pipeline registers are
  retained in the comparison and itemized when Lane 1 identifies data widths.

The same data buffer must not be counted as two physical arrays just because
two software queues reference it. Conversely, data cannot be unaccounted
between releasing a source slot and serving a future return/consumer.

## 6. Energy and delay method

Use measured event counts and technology-dependent per-event energies:

E_dynamic = n_RAMread·e_read + n_RAMwrite·e_write + n_copy·e_transfer
          + n_dirlookup·e_dir + n_meta_update·e_meta + n_arb·e_arb
          + n_lower_byte·e_lower_byte.

The units and event scopes must be explicit. Avoid double-counting a copy
whose RAM read/write already appear in the first two terms; e_transfer then
means wires/buffer only. Add leakage×elapsed time only from a matched physical
estimate. Lower traffic may rise under RO duplication, or fall under TVD;
neither direction is assumed in advance. No pJ or mW is filled without the
underlying macro/library estimates.

Delay paths to examine: Tag→payload selection; free/credit check→preview/commit;
TVD compare→valid-sector decision→Bank request; dirty forward eligibility before
WAD blocking; arbitrary Bank role mux; generation match on return. The allowed
TVD extra cycle is an architectural timing assumption, not timing closure.

## 7. RTL/synthesis availability audit and exact missing inputs

Read-only discovery found historical RTL at
`/workspace/repos/gpu-l2-cache-verilog-v3r2-clean`, HEAD
`f02733e51726d8d6e286a531b20a16aaeae11520` (historical V3-R2 work).
Yosys, Icarus, Verilator and OpenSTA are installed. Neither the frozen handoff
nor the received lane inputs binds this RTL to matched B16/U_WB16/TVD/RO
modules. Existing tools do not supply that equivalence. Therefore synthesis
of an unrelated historical top would not measure the EP-L2 delta and was not
run. This is `NO_MATCHED_CANDIDATE_RTL`, not `NO_RTL_ANYWHERE`.

Required before a valid changed-module differential synthesis:

1. Exact baseline and candidate RTL commits/module boundaries, with storage
   ownership/queue/port mapping to the simulated modes and parameter values.
2. Technology/cell and SRAM libraries (corners, voltage, temperature), macro
   choices, ECC policy and whether RAMs are macros or inferred registers.
3. Same synthesis/STA versions/options, clock period, uncertainty, IO loads,
   generated clocks and path exceptions; explain the physical meaning of an
   L2 modeled cycle separately from the 850MHz DRAM clock.
4. Role/generation/reference bounds, number of read/write/meta ports, lookup
   parallelism, arbitration depth and fairness design.
5. Baseline/candidate area reports, RAM bit/macro counts, critical paths,
   timing slack, and same-workload activity for any power claim.

When these exist, synthesize only changed modules and their necessary context
under identical constraints, preserve tool logs/checksums, report failing
constraints, then combine with unchanged/common blocks transparently.
