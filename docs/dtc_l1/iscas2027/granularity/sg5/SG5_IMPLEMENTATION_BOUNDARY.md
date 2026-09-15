# SG5 comparable lower-traffic observer: source design gate

The dedicated observer descendant shall add a single default-off parser flag,
`-gpgpu_l1_lower_traffic_observer`, default `0`.  It may allocate observer
counter state and print `SG5_*` fields only when enabled.  Its value must
never be read by cache admission, tag lookup, MSHR/PIB allocation, lower cap,
queue selection, request address/data size, response processing, or retirement.

The observer has three precise reporting families:

1. Conventional lower-read transactions and payload bytes, at the existing
   successful `baseline_cache::send_read_request` creation point.  The payload
   is the actual lower `mem_fetch` size after the existing atom-size rewrite.
2. DTC PAPER_IO/PAPER_OO lower transactions and payload bytes, at the existing
   post-construction `m_dtc_l1_{io,oo}_lower_created` point.  PAPER_IO and
   PAPER_OO each construct a 128-B lower request; MODERN_OO_SECTOR is reported
   separately and must never be conflated with PAPER_OO.
3. Diagnostic deltas for a pending hit (zero additional lower bytes) and the
   existing IO duplicate-after-eviction event (+128 bytes only when it reaches
   the existing `NEW_MISS` lower-create path).

No new counter may substitute for, rename, or reinterpret an accepted primary
performance counter.  The actual Core patch belongs only in a new SG5 observer
Core worktree descended from Core95; the current frozen Core and all accepted
runtime binaries remain untouched.

## Required directed fixtures once host admission is legal

| Fixture | Required observation |
| --- | --- |
| `sector32` | one S lower transaction; 32 payload bytes |
| `normal128` | one N lower transaction; 128 payload bytes |
| `dtc_io128` | one PAPER_IO NEW_MISS; one lower transaction; 128 payload bytes |
| `dtc_pending` | a pending Tag hit adds zero lower transactions and bytes |
| `dtc_duplicate` | duplicate-after-eviction adds exactly one 128-B IO lower request |
| `terminal_accounting` | created/issued/responded/payload accounting closes naturally |

NN and Btree must then prove OFF/ON equality of cycles, instructions, and all
pre-existing scientific counters for every supported mode before any G6
observer row is accepted.
