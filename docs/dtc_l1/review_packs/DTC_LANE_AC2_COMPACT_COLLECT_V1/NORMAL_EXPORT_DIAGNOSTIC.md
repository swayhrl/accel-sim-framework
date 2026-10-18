# Normal export diagnostic status

Compact production export: **UNAVAILABLE_SCIENTIFIC_STOP**. No observer, counter,
summary prefix or production printer is added. The existing K1 contract remains
byte-identical. All-OFF adds no pipeline/compact record. Existing AC ON prints
DTC_COLLECT_WB_V1 snapshots through actual gpu_print_stat(), with81920B/bank and
163840B total per SM; these must never be relabeled compact8KiB results.

The unchanged parent's strict parser is rerun on normal64-SM cumulative snapshots,
including empty SM sentinels and malformed/truncated/duplicate negatives. Last
complete population is used, snapshots are never added; a broken final snapshot
cannot fall back to an older one. UINT64_MAX means no sampled cycle, not time0.
The CPU capacity probe also invokes three actual normal statistics boundaries,
and confirms printing changes neither observer bytes, stage bytes nor clock.

The requested future compact diagnostics (eligible instructions, overflow/fallback
entries, bank sectors/bytes/owner occupancy, capacity backpressure, overlap cycles,
serial fallbacks, WB denials, stage entries/exits, first/last/sample boundaries)
remain requirements for a future implemented resource contract. No invented zero
rows stand in for unavailable counters. Any future version must define counts
versus cycles versus sector-byte occupancy, per-SM lifetime range, no-event
sentinels, and last complete64-SM snapshot parsing. Host printing overhead is not
GPU cycles, hardware area or a zero-delay implementation proof.
