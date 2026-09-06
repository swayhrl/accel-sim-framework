# M5.0BT — eight-workload repaired-Core replay plan

Status: **AUTHORIZED ACQUISITION PLAN; ATAX HARD GATE ACTIVE**.

## Scope

This is the researcher-authorized current replay batch: Paper-10 excluding
`2mm` and `syrk`.

| workload | current disposition | batch action |
| --- | --- | --- |
| BICG | post-repair T2 qualified | preserve; do not duplicate |
| ATAX | repaired-Core Base/IO/OO live | wait for one natural triplet closure |
| GEMVER | immutable payload; old-Core rows diagnostic only | repaired-Core triplet queued after the ATAX gate |
| MVT | immutable payload; old-Core rows diagnostic only | repaired-Core triplet queued after the ATAX gate |
| GESUMMV | immutable payload; prior Core diagnostic only | repaired-Core T3 triplet queued after the ATAX gate |
| SYR2K | local immutable receipt PASS | repaired-Core triplet queued after the ATAX gate and fresh heavy-slot check |
| SpMV | repaired-Core same-bundle strict triplet PASS | preserve; do not duplicate |
| 2DConv | accepted exact heavy-pilot immutable payload | repaired-Core triplet queued after the ATAX gate and fresh payload audit |

`2mm` is excluded only from this acquisition batch because it has
`ARCHIVE_ONLY_COPYBACK_SHA_PASS`, not the required formal immutable receipt.
`syrk` is excluded by the researcher batch selection. Neither exclusion
changes the all-ten M5.0BT completion contract, and neither payload may be
relabelled, deleted, or treated as a formal result.

## Non-bypass conditions

The source-correct lower-candidate-queue repair is Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`. Before any queued triplet is
launched, the live ATAX Base/IO/OO triplet must naturally terminate and pass
all of: strict parser, expected trace consumption, no assertion/fatal/
unclassified-deadlock/output-mismatch signature, lower create/issue/response
closure, dependency closure, and final PIB/inflight/lower (plus OO active-ref)
drain. This gate qualifies the repair; a host CPU slot alone is insufficient.

Every launched triplet must use one immutable workload bundle, Core `15cfa`,
the exact frozen Base/IO/OO config hashes, one runtime binary identity, and
three isolated output directories. Old-Core rows remain diagnosis evidence
only and are never relabelled.

## Dispatch order after ATAX PASS

1. Recalibrate the live pool: CPU quota/load, MemAvailable, swap `si/so`,
   iowait, output-space headroom, trace-store throughput and current p95 RSS.
2. Dispatch MVT and GESUMMV repaired-Core Base/IO/OO triplets first, as the
   lower-create repair qualification follow-up.
3. Dispatch GEMVER, SYR2K and 2DConv only up to the recalibrated worker and
   heavy-slot limits. A workload-local bundle/identity issue isolates that
   workload; it does not invalidate an already admitted independent triplet.
4. Natural terminal parsing and accounting close each row independently;
   triplet reuse remains conditional on all three matching rows and the
   relevant M5.0BT review gate.

This plan starts no new simulator and claims no stage PASS. It exists to make
the eight-workload acquisition reproducible once the running ATAX hard gate
closes.
