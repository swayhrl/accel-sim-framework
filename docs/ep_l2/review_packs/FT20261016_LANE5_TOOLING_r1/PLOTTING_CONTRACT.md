# Machine-readable output and metric contract for Lane 6

The result CSVs in this stage contain headers and no performance observations.
Do not plot empty cells as zero or announce a speedup from this tooling pack.
SOURCE_MANIFEST separates producing Core/Framework/binary identities from
publication, historical source and the frozen coordination document commit.

## Input and comparison identity

Run key covers producing Core SHA, Framework SHA, binary SHA256, ordered full
runtime config/auxiliary content and explicit environment, every trace body,
workload and epoch range, complete feature/ideal vector and termination contract.
Names alone never equate workload sizes. Preserve original case/size labels in
WORKLOAD_ROSTER. Full applications and diagnostic fragments are separate cohorts.
Lane 5 owns new B16 baselines shared with Lane 4; ideal diagnostics have their own
table and cannot fill implementation result cells.

First five workloads: convolutionSeparable, FWT_7_21, cfd_097k, vectorAdd_4M, sad.
Queue B16_BANKED/U_WB16 before TVD/RO. btree/dwt2d follow policy freeze; scan is
exclusive. Primary comparisons have 1168 physical 128B entries/slice and 4x292
banks. A conditional C8 comparison has 1160 entries and 4x290 banks on both arms.
No cross-budget speedup. Same-source, same-binary mode switches are preferred.

## Field scope and denominator

- cycles/instructions: native cumulative whole-GPU application values. Never
  sum application cycles across 64 slices or aggregate overlapping kernel deltas.
- unique_requesters/responses: exact epoch/slice/request identity cardinality;
  exactly one enqueue per accepted requester, separately from admission attempts.
  Matching total counts alone is not an exact-once proof.
- need/block: actual source-defined check/attempt events. Ratio block/need needs
  matching scope. Retry counts are not unique requests or elapsed stalled cycles.
- blocked/wait cycles: producer-defined observation domain. A sum of slice-cycle
  counters is labeled slice-cycles; report its corresponding eligible slice-cycle
  denominator. Never call that sum global GPU cycles.
- payload: mutually exclusive primary-owner role occupancies plus FREE equal
  the exact physical slot budget. Per-slot pins, pending sectors and reader refs
  are subordinate and not extra physical data items. Specify mean/time weighting.
- WB staging lifetime: actual readout/packet creation through actual lower
  acceptance with accounted downstream data storage. WAD lifetime ends at true
  writeback set_done; TVD post-accept retention is a separate lifetime/cost.
- static copy: charge resident read, WBUF write, lower-send WBUF read against
  the matched four-bank service. Unified in-place readout cannot gain free ports.
- bank operations/waits: role and read/write classes; one arbitrary line-sized
  operation/bank/cycle. Any aggregation records whether it sums all slices.
- lower traffic/bytes: source-defined real lower handoffs/data-bus events with
  read/write split. Retries and request multiplicity are not transferred bytes.
- native DRAM utilization: actual physical native counters; lower_admission
  normalization and queue occupancy are distinct metrics.
- TVD: valid requested-sector service, avoided real lower reads/bytes, dirty
  forwarding, promotion waits and additional retention. Missing-sector fallback
  must not be counted as a whole-line hit.
- RO: full-epoch oracle coverage/exclusions; real duplicate lower reads/bytes,
  descriptor/payload pressure and generation-safe detached completion. No blanket
  !is_write() eligibility and no fabricated oracle area estimate.

RESOURCE_MOVEMENT is long-form: run_key, workload, mode, metric, value, unit,
scope, denominator, source_field, source_sha256. Missing input remains absent
with explicit NOT_EMITTED/DEPENDENCY_PENDING explanations, never numerical 0.
Failed/time-out/incomplete rows remain in FAILURES_AND_PENDING and raw indexes,
excluded from means/geomeans. Report baseline_cycles/mechanism_cycles only for
qualified, equivalent inputs; the speedup field is a ratio, not percent.

## Conditional stronger controls

If U_WB16 exhibits a local effect, add a representative static 1024/112/32
partition (same 1168 total). Compute-only 1024/0/144 is labeled with its missing
bypass capability. Equal-copy-cost attribution and later mechanism x one-axis
headroom four-cell experiments are conditional; no such runs exist here.
