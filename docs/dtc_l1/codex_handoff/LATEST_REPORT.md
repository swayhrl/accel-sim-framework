# Latest Codex Report

## FAST64.3 Gaussian/Base and MRI-Q/Base strict terminals (2026-09-10)

Fresh immutable Gaussian/Base (`3ec79940-ae70-444a-8991-816d6f570223`) and
MRI-Q/Base (`4549f146-690a-4c32-be7f-ac8a8b363d3d`) both naturally exited `0`
and passed the future-only strict v2 collector with the frozen bbcbb/runtime/
A1/framework/Base-config identities. Gaussian records `4,229,815` cycles and
`283,685,120` instructions, lower acquire/release `1,951,815/1,951,815`, PIB
admit/retire `743,656/743,656`, terminal lower/PIB `0/0`, and cap-full `0`.
MRI-Q records `366,667` cycles and `1,411,757,056` instructions, lower
acquire/release `62,208/62,208`, PIB admit/retire `21,792/21,792`, terminal
lower/PIB `0/0`, and cap-full `0`. Both error scans are empty and their compact
strict/dynamic/structural evidence is retained under
`fast64/generated/fast64_3_dynamic_base_v1/` as
`STRICT_VALID_PENDING_STAGE_ACCEPTANCE`.

FAST64.3 is still active: 2DConvolution/Base remains live and Btree/Base is
queued behind its existing read-only continuation; no stage PASS is claimed.

## FAST64.4 Hotspot1 IO/OO source-reachable failure (2026-09-10)

Hotspot1 IO and OO physical precomputes remain preserved but are
non-authoritative failed attempts: their immutable-v2 attempts
`de96e9b8-eea8-4f2f-a179-b0d4b4a7f472` (IO) and
`0fdfa2a2-e9fb-427f-a8dd-97c412172ef8` (OO) each terminated `1` in seconds at
the same bbcbb `shader.cc:4279` `n_accesses > 0` assertion. They use the
frozen Hotspot1 payload, Core/runtime/A1/framework identities and distinct
correct IO/OO configs; they are not parser/accounting/results and will never
enter FAST64.4 aggregates. Hotspot1/Base with the same payload/identity is
strict-valid, isolating a mode-specific source-reachable empty-access issue.

The source-backed classification and isolated repair boundary are recorded in
`fast64/handoffs/FAST64_4_HOTSPOT1_ZERO_ACCESS_FAILURE.md`. Existing live
bbcbb rows and their frozen controllers are untouched. FAST64.1 and FAST64.2
remain closed (`FAST64_1_PLATFORM_PASS`, `FAST64_2_REPAIR_PASS`); FAST64.3 is
active and FAST64.4 is physical precomputation only.

The isolated minimal Core guard has now completed the exact Hotspot1 IO trace
naturally (`85,206` cycles; `377,291,004` instructions) with zero stderr,
closed lower/dependency accounting, and final IO PIB/inflight/lower `0/0/0`.
It is a repair qualification only, built from uncommitted isolated source and
therefore cannot be promoted or mixed with bbcbb formal evidence. A later
60-second one-worker audit passed (`swap_so_delta=0`, no OOM/PSI/throttle,
about 212 GiB cgroup headroom and 124 GiB output free), so the matching exact
Hotspot1/OO qualification is active in the fresh isolated namespace
`/workspace/fast64-repair-qual/hotspot1_oo_zero_access_guard_r0` on CPU 29.
It is likewise not a formal FAST64 row and has no result claim before natural
terminal lifecycle validation.

## FAST64.4 LUD IO/OO physical-precompute strict terminals (2026-09-10)

LUD/IO (`ad50c217-c4cc-4cf4-a514-91a368509f03`) and LUD/OO
(`ce6a4a2b-8986-4d3d-b8e0-c40f8141f76e`) naturally exited `0` and passed the
future-only v2 strict collector. Both preserve the frozen bbcbb/runtime/A1/
scientific-Framework/payload identities, one immutable execution epoch, empty
failure scans, lower create/issue/response conservation, dependency
create/complete conservation, and final PIB/inflight/lower state zero; OO also
ends with active refs zero. IO records `1,089,813` cycles and OO `1,086,338`,
each with `184,963,840` instructions. Their compact records are
`generated/fast64_4_precomputed_rows_v1/fast64_4_lud_{io,oo}_cap8192_a1_v3.json`.
They are strictly `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`: FAST64.4 has not
opened logically and no performance/triplet promotion is claimed.

## FAST64 future-wave parallelism recalibration (2026-09-10)

A read-only live inventory records 9 current FAST64 workers: 8 formal bbcbb
rows and the isolated Hotspot1/OO repair qualification. The formal-worker RSS
p50/p95/max is `644 MiB` / `4.79 GiB` / `4.79 GiB`; total live simulator RSS,
including two unrelated VM-TLB simulations, is about `18.0 GiB`. The cgroup
has a `384`-core quota, about `209 GiB` memory headroom, `~81 GiB`
MemAvailable, `~116 GiB` output capacity, zero CFS throttling and zero memory
PSI; iowait was `0.38%`. A 20-worker total FAST64 target is resource-safe by
the measured p95 planning model, subject to staged post-expansion evidence.

Future-only `util/dtc_l1/audit_fast64_future_precompute_resources_v2.sh`
supersedes v1 for new admission decisions. It retains every sampled
swap/major-fault/cgroup-I/O/PSI/OOM/CPU observation and classifies one positive
swap window as `TRANSIENT_SWAP_ACTIVITY`; only repeated positive windows are
`SUSTAINED_SWAP_ACTIVITY` and a pressure rejection. Its initial two-window
audit observed zero swap-out, major faults, PSI, OOM, and throttling. No live
controller or frozen closeout dependency was changed. To avoid avoidable Core
identity migration, unused capacity remains reserved for the Hotspot repair,
remaining Base work, and repaired-Core regression preparation rather than a
large old-bbcbb FAST64.4 wave before the repair is qualified.

## FAST64.3 active Base promotion / acquisition state (2026-09-10)

The exact-identity Base promotion audit accepts ATAX, BICG, GESUMMV, GEMM and
DWT2D (5/12), including BICG's separately extracted canonical-perf structural
companion. Historical NN Base was deliberately not reused because it lacks the
current frozen Framework execution identity. Its fresh immutable replacement
`fast64_3_NN_base_cap8192_a1_v2` naturally exited `0` and is strictly collected
with cycles/instructions `6,985/1,284,872`, lower `10,691/10,691`, PIB
`4,011/4,011`, final lower/PIB `0/0`, and lower-cap-full `0`; compact strict
and structural evidence is under `generated/fast64_3_dynamic_base_v1/`.
NN is `STRICT_VALID_PENDING_STAGE_ACCEPTANCE`, not a FAST64.3 PASS claim.

LUD/Base is now a second fresh strict-valid row, not yet a stage PASS claim:
immutable attempt `3a5f2814-bfb6-4f77-84c0-8c860d93b6e4` naturally exited `0`
and records `1,113,878/184,963,840` cycles/instructions, lower
`1,048,098/1,048,098`, PIB `373,488/373,488`, terminal lower/PIB `0/0`, and
lower-cap-full `0`.  Its compact strict, dynamic, and structural evidence is
`generated/fast64_3_dynamic_base_v1/fast64_3_LUD_base_cap8192_a1_v2.json`,
`FAST64_3_LUD_BASE_DYNAMIC_V1.tsv`, and
`FAST64_3_LUD_BASE_STRUCTURAL_METRICS_V1.json`.  The formal identity is the
frozen Core/runtime/A1/framework tuple and frozen LUD payload; its status is
`STRICT_VALID_PENDING_STAGE_ACCEPTANCE`.

Hotspot1/Base is a third fresh strict-valid row, also pending the full-stage
acceptance: immutable attempt `409dbf6b-9a36-41c8-8c34-4aad51e6154a` naturally
exited `0` with `160,486/377,291,004` cycles/instructions, lower
`701,725/701,725`, PIB `161,336/161,336`, terminal lower/PIB `0/0`, and
lower-cap-full `0`. Its compact evidence is the Hotspot1 triple under
`generated/fast64_3_dynamic_base_v1/`.  This is the frozen formal
Core/runtime/A1/framework identity and source payload, with status
`STRICT_VALID_PENDING_STAGE_ACCEPTANCE`.

2DConvolution/Base plus fresh Gaussian/Base and MRI-Q/Base are immutable and
CPU-active. Btree/Base remains reserved for the existing single-slot
continuation after 2DConvolution naturally terminates. No active row has an
assertion/fatal/actual-deadlock/output-mismatch signature.

The four-worker admission audit
`/tmp/fast64-future-wave4-audit-20260910T0807Z.tsv` passed: sampled swap-out,
OOM, memory-PSI and CFS throttling are zero; cgroup headroom is about 194 GiB
and output free space about 117 GiB. It admitted Gaussian (CPU 5), Hotspot1
(CPU 6), LUD (CPU 7), and NN (CPU 8) under distinct immutable attempt UUIDs.
This replaces the earlier arbitrary one-worker operational limit with a
measured-safe wave; it changes no scientific identity.

The generic v1 closeout monitor invokes the non-executable Python validator as
an executable and therefore cannot close a terminal row. It remains untouched
while live. Future-only `monitor_fast64_precomputed_row_v2.sh` invokes the
same frozen validator through `python3`; its static regression and NN
integration strict collection pass. This is a host-only controller repair, not
a parser/configuration/mechanism change.

The seven-row pool and every canonical workload dry-run pass using the
future-only alias-v3 validator, which keeps frozen validator/manifest bytes
unchanged and fixes lookup casing only. Two 60-second resource audits correctly
refused launch due to swap-out (`2289` for seven workers; `222` for one); no
FAST64 simulation was started and the shared VM-TLB jobs were not disturbed.

A subsequent one-worker audit passed with zero sampled swap-out and admitted
only the first missing Base row: 2DConvolution/Base in immutable namespace
`fast64_3_2DConvolution_base_cap8192_a1_v2`, attempt
`844f1ba7-58a9-4208-98e5-71e01b1a6885`, CPU 0. Its one-worker dynamic pool
exited after dispatch because it read the headered `supervisor_pid` field as
column one. The live immutable runner was not touched. Future-only
`continue_fast64_dynamic_pool_v3.sh` (SHA-256
`9fe78b45e048e97534cd4179b71d12b789a86d3c52cdabc91c6cdc678c6418c1`) now
adopts that live row read-only, corrects the header-aware receipt parse, and
will strict-validate its natural terminal before it refills Btree. No formal
result is claimed while the row is live. Separate future-only observer
`monitor_fast64_3_dynamic_base_evidence_v1.py` (SHA-256
`3d437ff5b8470ab0eee0ec1de576b6a7e6b601320e986d59c64df32a52ef7dd5`) waits
for that strict summary before materializing compact JSON/TSV evidence and its
source-defined Base structural companion; it never writes live run state.

The LUD natural terminal freed CPU 7.  A fresh measured admission audit
`/tmp/fast64-future-lud-terminal-refill-audit-20260910T082614Z.tsv` authorized
exactly one worker (zero sampled swap-out/OOM/PSI/throttle, about 190 GiB
cgroup headroom, and about 117 GiB output free).  It dispatched only
`fast64_4_lud_io_cap8192_a1_v3`, immutable attempt
`ad50c217-c4cc-4cf4-a514-91a368509f03`, on CPU 7 with a separate v2 collector.
This is physical precomputation under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; it is neither a FAST64.4 logical
opening nor an accepted performance row.

A second post-LUD/IO audit
`/tmp/fast64-future-post-lud-io-refill-audit-20260910T083209Z.tsv` again
admitted exactly one worker with zero sampled swap-out/OOM/PSI/throttle.
`fast64_4_2DConvolution_io_cap8192_a1_v3` is therefore active on CPU 16 under
immutable attempt `7ae2c41b-a4f1-444c-bade-ae93dbc6293e` and its independent
v2 collector.  It carries the same physical-precompute classification and is
not an accepted FAST64.4 row while live.

The next two-worker audit
`/tmp/fast64-future-two-worker-refill-audit-20260910T083444Z.tsv` also passed
with zero sampled swap-out/OOM/PSI/throttle.  It dispatched
`fast64_4_2DConvolution_oo_cap8192_a1_v3` on CPU 17 (attempt
`7e6c31bb-6887-4117-850c-6a3b2bc2764e`) and
`fast64_4_gaussian_io_cap8192_a1_v3` on CPU 18 (attempt
`5251ab7f-13b1-43dc-9b7d-0434ef498817`), each with a separate v2 collector.

The active FAST64.4 physical-only wave is ATAX/IO; GEMM/IO and GEMM/OO;
DWT2D/IO and DWT2D/OO; LUD/IO; 2DConvolution/IO and 2DConvolution/OO; and
Gaussian/IO.  Every member is an isolated immutable-v2 attempt under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; none is a logical FAST64.4 result
until the FAST64.3 gate and later primary-matrix acceptance both pass.

DWT2D/IO and DWT2D/OO have since naturally exited `0` and passed their
independent v2 strict collectors. Their immutable attempts are respectively
`257ccf84-1651-4116-a36d-b8227a4e1548` and
`8d866b57-202e-4386-b221-b1b418d68735`; both retain the frozen formal identity,
one execution epoch, clean failure scan, `148,684,429` dynamic instructions,
final lower `0`, and lower-cap-full `0`.  The IO row records `241,380` cycles
and zero IO lower-create-queue-full stalls; the OO row records `234,651`
cycles, zero OO lower-create-queue-full stalls, and final OO active refs `0`.
Their compact JSON evidence is retained under
`generated/fast64_4_precomputed_rows_v1/` as
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, not as an accepted FAST64.4 triplet.

After those DWT2D terminals, the four-worker audit
`/tmp/fast64-future-four-worker-refill-audit-20260910T083734Z.tsv` admitted a
new isolated wave: Gaussian/OO on CPU 22 (attempt `40293c57…`), Hotspot1/IO
on CPU 23 (attempt `de96e9b8…`), Hotspot1/OO on CPU 24 (attempt `0fdfa2a2…`),
and LUD/OO on CPU 25 (attempt `ce6a4a2b…`).  All four retain exact frozen
identity and independent immutable-v2 collectors, and all remain physical
precomputes pending FAST64.3 acceptance.

## FAST64.4 physical precompute — ATAX/IO active (2026-09-10)

A fresh 60-second `FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V1` admitted one
additional isolated worker (`swap_so_delta=0`, OOM/PSI/throttle deltas zero,
about 126 GB output free). The first ATAX/IO dispatch
`fast64_4_atax_io_cap8192_a1_v2` is retained as a non-authoritative
pre-simulation launch failure: it used a relative config path, so the
immutable runner changed to its run directory and the simulator immediately
exited `1` before an execution epoch. It produced no scientific result.

Its fresh repair `fast64_4_atax_io_cap8192_a1_v3` uses the same frozen,
absolute FAST64_IO config (SHA-256 `d4a2d9d0...`), payload, Core/runtime/A1
and framework identities; immutable attempt
`105ec7d4-8330-4493-b09a-0f3c2b6d402d` runs on CPU 3 under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`. It is physically acquired only:
FAST64.4 is not logically open and no result is claimed while live.

## FAST64.2 repair qualification PASS (2026-09-10)

FAST64.2 is `FAST64_2_REPAIR_PASS`. The source-reachable diagnostic
`fast64_2_nn_io_coupled_cap1_pib1_a1_v1` naturally exited `0` under the
immutable-v2 receipt chain and strict validation. Its diagnostic-only cap-1,
IO-entries-1 overlay records `31,399,562` global lower-cap-full events and
`31,105,381` IO lower-create-queue-full stalls, while closing lower
create/issue/response at `2,673/2,673/2,673`, dependencies at `5,346/5,346`,
and final inflight/PIB/lower state at `0/0/0`. It has `564,234` cycles and
`1,284,872` instructions, with an empty assertion/fatal/actual-deadlock/output
mismatch scan.

The cap-1 row is a source-backed diagnostic only: it does not alter the
formal 8192-cap platform or enter performance aggregates. The retained
high-cap BICG negative control and immutable R2 BICG Base/IO/OO normal-triplet
reuse complete the FAST64.2 acceptance set. Compact evidence and the full
checklist are in `fast64/handoffs/FAST64_2_REPAIR_QUALIFICATION.md` and
`fast64/generated/fast64_2_coupled_stress_cap1_v1/`.

## FAST64.1 immutable R2 full-wave PASS (2026-09-10)

FAST64.1 is `FAST64_1_PLATFORM_PASS`. All seven immutable-v2 R2 rows naturally
exited `0`, have one atomic START/TERMINAL attempt UUID and one natural-exit
epoch, and strict-validate with formal Core `bbcbb5e...`, runtime
`6a8743b4...`, A1 observer `2c2a6a27...`, scientific Framework snapshot
`037f008b...`, the frozen payload, and resolved config identity. Required
terminal lower/dependency/drain state is closed and error scans are clean.

R2-vs-R2 BICG/IO, BICG/OO, and GESUMMV/IO 8192-vs-high comparisons are each
`EXACT_METRIC_MATCH`; every required 8192 candidate records
`DTC_L1_lower_cap_full_events = 0`. This freezes the unchanged 64x1 platform,
payload, DTC configuration, and cap-8192 non-binding conclusion.

The frozen full-wave reader was preserved unchanged and fail-closed on its
known alias defect: it counts the normal `perf_counter.csv.gz` symlink as a
second perf stream. Its final retained log SHA-256 is
`f3c1cd810d4d86d6a62274655b855967e6994abb84b850d1f84e65f7ba545ea2`.
Future-only alias-v2 verifies that each optional alias resolves to the one
canonical timestamped stream, preserving—not weakening—single-epoch proof.
The compact row JSONs, comparison TSVs, PASS marker, and SHA manifest are in
`fast64/generated/qualification_r2_full_wave_alias_v2/`.

FAST64.2 is now active. The existing coupled stress remains strict-negative
pressure evidence; no FAST64.2 PASS is claimed. Disk headroom is about 45 GiB
at 99% use, so storage inventory/retention proof is the immediate operational
task before any large later-stage wave.

## FAST64.3 ATAX/Base natural terminal — strict-valid precompute (2026-09-09)

The future-only immutable-v2 ATAX/Base precompute
`fast64_3_precomputed_atax_base_cap8192_a1_r2` naturally exited `0` at
`2026-09-09T01:26:57Z`.  Its separate alias-aware v3 collector records one
immutable attempt (`2e51d286-4483-45fd-8795-dd19fcd413c4`), normal simulator
exit, an empty precise assertion/fatal/deadlock/output-mismatch scan, and one
canonical perf epoch (with the normal alias normalized).  The bound identity
is Core `bbcbb5e...`, runtime `6a8743b4...`, A1 observer `2c2a6a27...`,
execution snapshot `037f008b...`, Base config `1a016e3c...`, and frozen ATAX
trace-list `b6dcd0e3...`.

Compact evidence under `fast64/generated/fast64_3_atax_base_alias_v3/` closes
lower acquired/released at `19,215,755/19,215,755`, PIB admits/retires at
`3,145,984/3,145,984`, and terminal lower/PIB at `0/0`; it records
`87,750,512` cycles and `145,666,048` instructions.  The structural companion
keeps cacheline allocation (`1,349,272,650`), MSHR-entry (`0`), miss-queue
(`1,070`), and Tag-bank (`20,972,288`) categories distinct.  Its sole status
is `FAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE`:
this neither promotes FAST64.3 nor authorizes IO/OO work.

The FAST64.1 R2 closure is unchanged: it remains **5/7** terminal, with both
GESUMMV IO rows CPU-active and the frozen closeout controller waiting.  A
fresh resource audit is fail-closed for another worker (swap essentially full,
load above the 512 logical CPUs, and only about 56 GiB output free), so neither
the optional FAST64.2 stress nor another FAST64.3 row is launched.

## FAST64.2 BICG coupled stress and FAST64.3 GEMM/Base terminals (2026-09-08)

The immutable BICG/PAPER_IO coupled-stress fallback (`cap=512`, source-coupled
IO PIB entries `1`) naturally exited `0` at `2026-09-08T21:51:34Z`. Its
future-only alias-aware collector proves one immutable epoch, exact frozen
identity, clean failure scan, lower create/issue/response conservation
(`17,607,590` each), dependency conservation (`18,350,080` each), and final
IO inflight/PIB/lower `0/0/0`. Both required pressure observations remain zero:
`DTC_L1_lower_cap_full_events=0` and
`DTC_L1_io_lower_create_queue_full_stalls=0`. It is therefore
`FAST64_2_BICG_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT`, not a
FAST64.2 PASS; compact evidence is
`fast64/generated/fast64_2_coupled_stress_bicg_alias_v2/`.

GEMM/Base also naturally exited `0` at `2026-09-08T23:15:14Z` and is strictly
valid only as FAST64.3 physical precomputation: cycles/instructions
`2,662,394/739,246,080`, lower acquired/released
`16,813,388/16,813,388`, PIB admits/retires `12,599,296/12,599,296`, final
lower/PIB `0/0`, and lower-cap-full `0`. Its independent future-only v4
collector and structural companion are compact evidence under
`fast64/generated/fast64_3_gemm_base_alias_v4/`; this does not promote
FAST64.3 or authorize an expanded batch.

The fresh resource audit is fail-closed for additional work: swap is fully
used, load is about `569` on `512` logical CPUs, and output free space is
about `55 GiB`. No new worker is launched. The frozen FAST64.1 R2 closure
bytes retain their recorded hashes; R2 remains **5/7** natural terminals with
the two GESUMMV IO rows live and the unmodified frozen controller waiting.

## FAST64.1 fifth immutable-R2 natural terminal (2026-09-08)

`fast64_1r2_bicg_io_cap1048576_a1` (BICG / PAPER_IO / cap 1048576)
naturally exited `0` at `2026-09-08T22:48:52Z`. Its atomic immutable-v2
START/TERMINAL receipts agree on attempt
`661b4953-6045-4bc6-8943-9a0f6d90c35b` and runner `bf9a84c8...`; the
manifest binds Core `bbcbb5e...`, runtime `6a8743b4...`, A1 observer
`2c2a6a27...`, execution snapshot `037f008b...`, frozen IO-high-cap config
`c0d169b8...`, and canonical BICG trace-list `388740a7...`. The simulator
emitted its normal exit sequence, and the precise assertion/fatal/deadlock/
output-mismatch scan is clean.

R2 receipt state is now **5/7 natural terminals**, with GESUMMV
IO@8192/@1048576 remaining live. The frozen R2 controller remains untouched
and is the sole authoritative full-wave collector after 7/7. This is a
pending natural-terminal observation only, not individual strict validation,
cap-comparison acceptance, or FAST64.1 PASS.

## FAST64.1 fourth immutable-R2 natural terminal (2026-09-08)

`fast64_1r2_bicg_oo_cap8192_a1` (BICG / PAPER_OO / cap 8192) naturally
exited `0` at `2026-09-08T18:43:49Z`.  Its atomic immutable-v2 terminal
receipt identifies attempt `89d2c798-e66c-4e8d-8dfd-df26d01ff9f7`, runner
`bf9a84c8...`, Core `bbcbb5e...`, runtime `6a8743b4...`, A1 observer
`2c2a6a27...`, execution snapshot `037f008b...`, frozen OO config
`546c68f9...`, and canonical BICG trace-list `388740a7...`.  The direct
simulator emitted the normal exit sequence, and the precise assertion/fatal/
deadlock/output-mismatch scan is clean.

R2 receipt state is now **4/7 natural terminals**, with BICG IO@1048576 and
GESUMMV IO@8192/@1048576 remaining live.  The frozen R2 controller is still
the sole authoritative full-wave collector after 7/7; this is only a pending
terminal observation, not individual strict validation, a comparison result,
or FAST64.1 PASS.

## FAST64.1 third immutable-R2 natural terminal (2026-09-08)

`fast64_1r2_bicg_oo_cap1048576_a1` (BICG / PAPER_OO / cap 1048576)
naturally exited `0` at `2026-09-08T18:19:06Z`.  Its atomic immutable-v2
terminal receipt is chained to attempt
`26b9fab6-0138-4750-923d-3d79a4b7f9df`, runner `bf9a84c8...`, Core
`bbcbb5e...`, runtime `6a8743b4...`, A1 observer `2c2a6a27...`, execution
snapshot `037f008b...`, its frozen OO-high-cap config, and the canonical BICG
trace-list SHA-256 `388740a7...`.  The direct simulator emitted its normal
exit sequence, stderr is empty, and the precise assertion/fatal/deadlock/
output-mismatch scan is clean.

This changes the R2 receipt state to **3/7 natural terminals**, with the four
remaining R2 rows still live.  The frozen R2 closeout controller remains
untouched and will perform the only authoritative strict collection after all
seven terminal receipts exist.  Consequently this record is a pending
natural-terminal observation, not individual strict validation, cap-comparison
acceptance, or a FAST64.1 PASS claim.

## FAST64 review-time safe-parallelism audit (2026-09-08)

The requested post-seven-row-R2, 60-second read-only admission audit is
`/tmp/fast64-post-r2-fullwave-safeparallel-audit-20260908T181439Z.tsv`.
It authorizes exactly one additional worker: zero sampled swap-out, cgroup
OOM, memory PSI, and CFS throttling; 245 available distinct physical-core
candidates; 197,735,043,072 bytes cgroup memory headroom; and
61,653,282,816 bytes output free space.  The five live R2 simulators remained
near one CPU core each during this observation.  This is an operational
capacity result, not a FAST64.1 acceptance result.

No duplicate NN coupled-stress process was launched.  The specifically named
NN/PAPER_IO, cap-512, PIB-1 immutable-v2 row already naturally exited `0` with
the exact frozen Core/runtime/A1-observer/config identity and was strictly
collected as `FAST64_2_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT`: both
required pressure counters were zero.  Repeating the identical NN row would
not add evidence.  Its authorized BICG/PAPER_IO fallback under the same
cap-512/PIB-1 source-coupled configuration was then live in an isolated
immutable-v2 namespace.  This is a historical launch snapshot: the BICG
terminal strict-negative result and GEMM/Base terminal are recorded at the top
of this report; only ATAX/GESUMMV Base remain live.  Nothing in the frozen R2
closeout dependency closure, any R2 process, or any active monitor was
changed.

## FAST64.3 DWT2D/Base strict-valid precompute (2026-09-08)

The isolated DWT2D/Base immutable-v2 row naturally exited `0` at
`2026-09-08T17:40:19Z`.  Its future-only v3 collector produced only compact
evidence under `fast64/generated/fast64_3_dwt2d_base_alias_v3/`: one canonical
perf epoch (with the normal alias normalized), exact frozen identity, positive
progress (`344,119` cycles; `148,684,429` instructions), lower
acquired/released `757,359/757,359`, PIB admits/retires `437,886/437,886`, and
terminal lower/PIB state `0/0`.  The precise failure scan is clean.  Its sole
status is `FAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE`;
it is not a FAST64.3 PASS and it authorizes neither later-stage IO/OO rows nor
a performance claim.

A separate future-only structural-metric extractor now reads only the
canonical terminal perf row, leaving the frozen R2 parser unchanged.  Its DWT2D
regression resolves the relevant category semantics from Core source:
`LINE_ALLOC_FAIL` means conventional L1D cache lines are all reserved and is
not interchangeable with the diagnostic Tag-bank conflict counter.  The
compact companion records line-allocation `1,417,779`, MSHR-entry-full
`346,268` (exactly cross-checked with the terminal summary), MSHR-merge-full
`0`, downstream miss-queue-full `18,367`, and the already closed Base
lower-request lifecycle.  This improves future FAST64.3 metric completeness
only; it does not promote DWT2D or alter any live row.

The future-only structural-companion monitor is now prepared for ATAX,
GESUMMV, DWT2D and GEMM.  It requires a natural terminal receipt plus the
existing strict Base JSON before it extracts a companion exactly once; it
cannot create Base validity evidence or alter any active Base/R2 monitor.  Its
static/once regression confirms that live rows remain waiting-only and have no
premature companion output.

The current 60-second, read-only post-review admission audit was fail-closed:
although swap-out/OOM/throttling were zero and cgroup/output headroom remained
ample, `memory_psi_avg10=0.01`, so `safe_to_launch=NO`.  No replacement worker
was launched.  The seven R2 closeout bytes and live simulators remain
untouched.

## FAST64.3 GEMM/Base controlled replacement admission (2026-09-08)

After DWT2D naturally freed its worker, a new 60-second read-only resource
audit passed exactly one replacement: zero sampled swap-out/OOM/memory PSI/CFS
throttling, 246 candidate physical cores, 207.4 GiB cgroup headroom and 62.6
GiB output space.  The immutable-v2 dispatcher admitted only
`fast64_3_precomputed_gemm_base_cap8192_a1_r2`, GEMM/Base, at
`2026-09-08T17:45:33Z` on CPU 11 with UUID
`4b62ba62-9ee3-41ed-8a67-402172e594fa`.  This is a historical admission
snapshot; GEMM subsequently reached its terminal strict-valid precompute
state, recorded at the top of this report.

The existing live v3 monitor is left untouched.  A separate future-only GEMM
v4 collector/monitor pair passed static regression and waits only for GEMM's
atomic terminal receipt.  It cannot affect R2 or any active v3 row.  GEMM is
strictly `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`, not a formal result or
stage advancement.

The first GEMM v4 monitor exited after its inherited caller stdout closed; its
simulator stayed CPU-active and untouched.  A bounded read-only reproduction
proved the monitor loop itself correct.  The same committed monitor was
relaunched in an independent session with stdout/stderr redirected to
`/dev/null`, retaining only its explicit log channel.  It survived a full
120-second poll and recorded the next wait state.  This is solely a monitor
lifecycle recovery, with no collection/promotion claim and no R2 dependency
change.

## Future-only FAST64.4 triplet consistency preflight (2026-09-08)

`validate_fast64_triplet_v1.py` now provides a fail-closed compact-JSON
validator for a later Base/IO/OO triplet.  It validates common payload and
trace-list identity, dynamic instruction-domain equality, per-mode drain and
conservation, and—in formal mode—immutable receipts plus common runtime/A1
observer identity.  Its synthetic immutable-fixture regression passes and its
deliberate instruction-mismatch fixture fails.  It is not connected to a live
controller and cannot promote any current precompute or stage.

## FAST64 controlled third Base admission and Base closeout recovery (2026-09-08)

A new 60-second post-small-batch audit at
`/tmp/fast64-post-smallbatch-resource-audit-20260908T172527Z.tsv` authorized
exactly one worker: it recorded zero swap-out/OOM/memory PSI/CFS throttling,
205.8 GiB cgroup memory headroom, and 62.7 GiB output space.  The immutable-v2
Base dispatcher therefore admitted DWT2D/Base only, on CPU 11, into
`fast64_3_precomputed_dwt2d_base_cap8192_a1_r2` at
`2026-09-08T17:26:51Z` with UUID
`adc75323-a985-4222-bc28-804e4a9dedad`.  Its START receipt and frozen identity
chain are present; it is CPU-active and classified solely as
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`.

Read-only source/log inspection found that the active v2 ATAX/GESUMMV Base
collectors' broad `deadlock` pattern matches the normal
`-gpgpu_deadlock_detect` configuration-help echo.  The active monitor was not
edited.  Separate v3 collector/monitor files now use precise diagnostic
patterns and independently wait for atomic terminal receipts for ATAX,
GESUMMV, and DWT2D.  Their pre-terminal regression passed.  No Base result is
promoted and no R2 closeout byte or live simulator was changed.

## FAST64 frozen R2 alias defect and F2 negative evidence (2026-09-08)

The frozen R2 validator's single-epoch glob counts a normal simulator symlink
alias (`perf_counter.csv.gz`) in addition to its sole timestamped perf stream.
Read-only inode/initialization evidence proves this is one epoch, but the
frozen validator rejects it as two streams. The frozen R2 collector also asks
the parser for lower-cap configuration, although the cap is source/config
identity rather than a terminal metric. Neither frozen byte was changed. A
versioned alias-aware reader is prepared and documented in
`fast64/handoffs/FAST64_1_R2_PERF_ALIAS_VALIDATOR_RESOLUTION.md`; it may only
become relevant after the existing frozen controller has fail-closed at 7/7.

The newly acquired immutable FAST64.2 NN/IO coupled stress has now been
strictly collected with a future-only alias-aware reader. It naturally exited
0, has one immutable epoch, exact identity, lower create/issue/response
conservation (`2673`), dependency conservation (`5346`), and drained final
state. Its required pressure events are both zero
(`lower_cap_full_events=0`, `io_lower_create_queue_full_stalls=0`), so it is
`FAST64_2_COUPLED_STRESS_STRICT_NEGATIVE_PRESSURE_ABSENT`, not FAST64.2 PASS.
The compact evidence is
`fast64/generated/fast64_2_coupled_stress_alias_v2/`; this ordinary
source/configuration-pressure diagnosis does not alter R2 semantics or any
frozen closeout dependency.

A later fresh 60-second admission at
`/tmp/fast64-future-precompute-audit-20260908T164959Z-for-f2-recheck.tsv`
returned `safe_to_launch=YES` for exactly one worker: sampled swap-out,
cgroup OOM and memory PSI were zero, with 191.8 GiB cgroup headroom and 58.5
GiB output space.  The researcher-authorized BICG fallback is therefore now
physically acquired, not inferred: `fast64_2_precomputed_bicg_io_coupled_cap512_pib1_a1_r2`
started at `2026-09-08T16:51:44Z` on CPU 9 with immutable attempt UUID
`24e4fff0-e2c5-4832-b8d6-fec5ae911249`.  This is a historical launch snapshot:
the row subsequently naturally terminated and was strictly collected as the
negative-pressure result recorded at the top of this report.  It has no
FAST64.2 PASS or R2-dependent stage transition claim.

The BICG row also has a dedicated future-only closeout monitor.  It observes
only the immutable terminal receipt, then invokes the existing BICG strict
collector once and checks for its compact evidence; it cannot launch, signal,
restart or promote a row.  Its once-mode pre-terminal regression confirms that
it only records a wait state before a terminal receipt exists.

## FAST64.3 controlled two-row Base precompute, pending (2026-09-08)

`prepare_fast64_3_base_precompute_v2.sh` is a future-only immutable-v2,
topology-aware one-row Base dispatcher. It permits only the ten nonredundant
FAST12 candidates while preserving potential BICG/NN evidence reuse. Its ATAX
dry-run passed. The earlier rejected audit is retained as evidence; a later
60-second audit at
`/tmp/fast64-future-precompute-audit-20260908T153334Z.tsv` observed zero
swap-out/OOM/memory-PSI/throttling, 249 distinct physical-core candidates, and
adequate memory/output headroom, returning `safe_to_launch=YES` for exactly
one worker. It admitted only `fast64_3_precomputed_atax_base_cap8192_a1_r2`
on CPU 0, with immutable runner UUID
`2e51d286-4483-45fd-8795-dd19fcd413c4` and classification
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`. The START receipt exists and the
initial failure scan is empty. This live row remains nonformal pending work and
cannot advance FAST64.3 or interfere with FAST64.1 R2 closeout.

The final frozen A1 `runtime_stat=500000` has flag zero: it suppresses
human-readable runtime-stat output but emits a perf-counter stream only after
each 500,000 simulated-cycle boundary. Before that first boundary, host
CPU-time progress was the available liveness evidence.

ATAX has since crossed two perf boundaries (500,000 and 1,000,000 simulated
cycles; 386,656 and 675,008 instructions).  Its provisional launch-to-second-
point lower-bound rate is about 1,299 cycles/s and 877 instructions/s, while
all five R2 workers retained about 99.4--99.5% CPU.  The required fresh expansion audit
nevertheless failed solely on `swap_so_delta=103`, so no second Base worker
was launched.

A subsequent independent 60-second admission audit at
`/tmp/fast64-future-precompute-audit-20260908T155148Z-after-atax15m.tsv`
returned `safe_to_launch=YES` for exactly one additional worker: zero sampled
swap-out/OOM/memory-PSI/throttling, 181 GiB cgroup memory headroom and 57.5
GiB output space.  It was taken only after ATAX had crossed its 1,500,000-cycle
perf boundary and the five live R2 simulators remained CPU-active.  The
future-only dispatcher then admitted exactly one nonredundant row,
`fast64_3_precomputed_gesummv_base_cap8192_a1_r2`, on CPU 3 at
`2026-09-08T15:53:37Z`; its immutable attempt UUID is
`c4d6d35e-23ad-4466-b578-ed1f00eb2ee9`.  Its START receipt and source identity
chain are present, its simulator is CPU-active, and its initial
assertion/fatal/deadlock/error scan is clean (apart from configuration help
text mentioning the deadlock flag).  This is the only expansion: it remains
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`, has no formal performance claim,
and does not alter any frozen R2 byte or controller.

The new GESUMMV row now has its own future-only strict collector,
`collect_fast64_3_gesummv_base_alias_v2.sh`.  It is deliberately separate from
all R2 closeout bytes and rejects before creating output unless a natural
terminal receipt exists.  Static syntax validation and a live-row
pre-terminal invocation both passed this fail-closed check; no run-directory
file or result artifact was created.  At natural terminal it will require the
immutable identity tuple, Base/cap identity, lower-credit and PIB
conservation, zero final lower/PIB state, positive cycle/instruction progress,
and an assertion/fatal/deadlock/output-mismatch scan before it can record only
the still-pending precompute classification.

A separate future-only Base closeout monitor is now prepared for the active
ATAX and GESUMMV namespaces.  It treats only an atomic `RUN_TERMINAL.tsv` as a
trigger, then invokes the corresponding strict pending collector once; it has
no launch, signal, restart or R2-closeout capability.  Its once-mode regression
proves pre-terminal rows are only observed, not collected.  It remains a
pending-evidence convenience and cannot promote FAST64.3.

For later post-FAST64.2 formal waves, the legacy mutable dynamic pool is now
explicitly superseded for future use by separate
`dispatch_fast64_precomputed_row_v2.sh` and `run_fast64_dynamic_pool_v2.sh`
files.  They verify the read-only SHA-addressed runner, runtime/Core/observer
and scientific-config identities, atomic immutable-v2 receipts and the R2
trace-config identity; they neither reference nor change the frozen R2
closeout bytes.  Their dry-run regression proves that a pending Base wave can
be planned without creating a namespace and that IO is refused before
FAST64.2 PASS.  No formal row was launched and no stage authority changed.

## FAST64.1 R2 closeout freeze and first natural terminals (2026-09-08)

The seven-row R2 closeout dependency closure is now frozen, byte-addressed in
`fast64/handoffs/FAST64_1_R2_CLOSEOUT_DEPENDENCY_FREEZE.md`, and must remain
unchanged until the existing closeout controller publishes
`FAST64_1_R2_FULL_WAVE_COLLECTOR_PASS`. This includes the controller,
collector, parser/validator/cap comparator, payload manifest, all R2 configs,
and R2 `trace.config`. Future work must use versioned controllers and only
read these bytes.

Two cohort-1 rows have naturally reached immutable terminal exit 0: BICG
Base@8192 at `2026-09-08T12:56:42Z` and BICG IO@8192 at
`2026-09-08T13:08:48Z`. Their receipt UUID/immutable-runner chain is intact;
the error scan found only configuration text and zero-valued invariant prints.
The five continuation R2 rows remain CPU-active. The untouched closeout
controller has observed `2/7` terminal receipts and remains the only route to
strict collection or FAST64.1 promotion.

## FAST64.1 five-row immutable-R2 continuation authorized (2026-09-08)

The researcher superseded the bootstrap two-worker ramp and authorized an
immediate five-row continuation wave, while preserving the two live cohort-1
R2 process trees and all existing SHA-pinned controllers unchanged. A new,
future-only one-shot dispatcher has a separate continuation lock and a fixed
five-row scope; it cannot touch the two existing namespaces. It verifies the
same immutable-v2 runner, Core/runtime/A1 observer/scientific-config identity
tuple, frozen config bytes, fresh namespace absence, unique UUID, atomic
receipts, and topology-aware explicit CPU placement.

The fresh 60-second cgroup audit at
`/tmp/fast64-r2-continuation-resource-audit-20260908T123617Z.tsv` passed full
five-worker admission: 12.822 useful core equivalents under a 384-core quota,
zero throttling/swap-out/OOM/memory-PSI, 252 distinct physical-core candidates,
18,647,875,584-byte 5+1 RSS requirement versus 203,603,755,008-byte cgroup
headroom, and 67,846,701,056 output-free bytes. Host loadavg is supplemental,
not a mixed-scope cgroup rejection. See
`fast64/handoffs/FAST64_1_R2_FULL_WAVE_CONTINUATION.md`. Admission is
authorized; dispatch receipts determine the next execution-state update.

The dispatch succeeded at `2026-09-08T12:41:22Z`: all five fixed future-only
rows received fresh immutable START receipts, so the complete R2 wave is now
**7/7 LIVE**. The rows are BICG OO@8192, BICG IO@1048576, BICG OO@1048576,
GESUMMV IO@8192, and GESUMMV IO@1048576, pinned to topology-selected CPUs
5/6/7/8/10. Their runner/Core/runtime/A1/scientific-config tuple exactly
matches cohort 1. The original Base@8192 and IO@8192 rows were neither opened
nor altered. A short follow-up found all seven direct simulator children in
state `R` at about 99% CPU, no growth in swap-out or OOM totals, zero memory
PSI and zero cgroup throttling. The two cohort-1 perf streams had progressed
to 82.0M and 88.0M cycles; new rows are live, not yet terminal results.

The existing autorefiller observed seven namespaces and recorded
`FAST64_R2_AUTOREFILL_DISPATCH_COMPLETE` at `2026-09-08T12:42:26Z`; it did not
create duplicates. The untouched strict closeout controller remains waiting
for 7/7 terminal receipts. FAST64.1 is still stage-gated pending natural
terminal/strict collector/comparison evidence. Compact per-row UUID/PID and
follow-up evidence is in `fast64/handoffs/FAST64_1_R2_FULL_WAVE_CONTINUATION.md`.

## FAST64.1 R2 dispatch-lock inheritance recovery (2026-09-08)

The first two immutable R2 supervisors inherited the dispatcher's advisory
lock descriptor.  Read-only `fuser` and `/proc/<pid>/fd/9` evidence ties the
lock to both live supervisor/process trees; this is an execution-controller
lifetime defect, not a simulator, DTC, configuration, or scientific-identity
defect.  The live rows are preserved untouched: there is no safe in-place FD
closure that does not perturb production processes, so the current lock will
release only when those rows naturally reach their terminal state.

The future-only dispatcher now closes FD 9 before `setsid` creates a detached
supervisor.  A disposable lock/sleep topology regression proves that the child
remains live while a second dispatcher can acquire the advisory lock; the
existing namespace mkdir, immutable SHA binding, UUID, receipts, and
single-epoch validator are unchanged.  This removes the issue for all rows
launched after the two live rows.  Status is
`FAST64_1_R2_RESOURCE_ADMISSION_PENDING` solely for this bounded lock lifetime;
FAST64 Goal execution remains active.  On either natural terminal event, take
a fresh resource audit and admit the next frozen-priority missing R2 row.
A low-frequency host-only `monitor_fast64_1_r2_autorefiller.sh` is active in
the `fast64-r2-autorefiller` persistent tmux controller: it holds a separate monitor lock, pins the reviewed
dispatcher SHA, waits for the live dispatch lock to disappear, performs the
same 60-second read-only audit, and invokes the dispatcher only for a fresh
`YES` admission.  It exits fail-closed on dispatcher-source drift and does not
inspect, signal, alter, or collect an existing R2 namespace.

A separate `fast64-r2-closeout` persistent tmux controller now waits only for
all seven fixed R2 terminal receipts.  It is SHA-pinned to the existing
fail-closed R2 collector, invokes that collector only after all seven rows are
terminal, and atomically publishes an external collector-pass marker only on
strict success.  It never launches or alters a simulator, and a collector
failure remains a retryable evidence failure rather than a stage promotion.

## FAST64.1 topology-aware R2 admission is ready (2026-09-08)

The remote review supersedes the former fixed/exclusive `74-80` pool rule:
host CPU placement is scheduling metadata, never a FAST64 scientific identity.
The dispatcher now uses `lscpu -p=CPU,CORE,SOCKET,NODE` and live affinity data,
prefers distinct physical cores, excludes only singleton/narrow pinned
simulator affinity, and ranks remaining candidates by current scheduler
occupancy.  A broad `Cpus_allowed_list=0-511` is soft host contention, not
exclusive ownership of every CPU.  R2 remains explicitly `taskset` pinned;
all immutable-v2, SHA, UUID, namespace, receipt and strict-validator guarantees
are unchanged.

`audit_fast64_r2_resources.sh` remains read-only but now publishes the
required `FAST64_R2_RESOURCE_AUDIT_V1`, including topology candidates, realistic
live p95 RSS and historical-R1 output footprint, cgroup/swap/OOM/PSI/I/O
deltas, and autonomous `safe_to_launch` / `authorized_workers` N_safe decision.
It never launches a process.  A passing audit authorizes the dispatcher to
admit the frozen-priority missing R2 rows without waiting for historical R1
termination; a conservative one-to-two worker ramp remains the policy.

The first formal immutable R2 ramp was admitted at `2026-09-08T04:06:56Z`
from `/tmp/fast64-r2-resource-audit-launch-v2.tsv`: `safe_to_launch=YES`,
`authorized_workers=2`, 384 cgroup quota cores, 249 available distinct
physical-core candidates, 9 pre-launch simulators, p95 RSS 8,925,478,912
bytes, 139,714,740,224 bytes MemAvailable, zero swap-out/OOM/throttling/PSI/iowait and
45,600,477,184 bytes output free.  The sample's 30-page swap-in without swap-out or PSI
is recorded but is not active pressure.  The new live rows are BICG
Base@8192 (`fast64_1r2_bicg_base_cap8192_a1`, CPU 0, UUID
`0c84f039-346e-4d28-9d0f-b7a4e04ee8b0`) and BICG IO@8192
(`fast64_1r2_bicg_io_cap8192_a1`, CPU 3, UUID
`81a1e97c-af78-417d-a38a-440a0a43ccd7`).  Both have immutable runner SHA
`bf9a84…`, exact Core/runtime/A1/scientific-config provenance and published
`RUN_START.tsv`; neither is terminal or promotable yet.

## FAST64.2 forced lower-create stress decision resolved (2026-09-08)

The one high-cap BICG/PAPER_IO diagnostic has naturally terminated with a
clean single execution epoch, exit 0, exact lower create/issue/response
conservation, and drained final state.  It is **not** FAST64.2 PASS: its
source-coupled entries-one overlay recorded
`DTC_L1_io_lower_create_queue_full_stalls = 0`.

Frozen-Core source sequencing explains why the former high-cap positive retry
was invalid:
PAPER_IO produces at most one candidate per SM cycle, and the following
cycle's pre-memory-stage issue routine removes it whenever the high global cap
has credit.  The NoC-full path only retains a separate unbounded issue queue.
Hence the former high/non-binding-cap plus natural queue-full requirement was
incompatible with this PAPER_IO path.  Researcher-authorized Option 2 now
classifies the completed row as `FAST64_2_HIGH_CAP_NEGATIVE_CONTROL` and
prepares an immutable NN/IO `cap=512, PIB=1` source-reachable coupled positive
stress.  The run remains resource-gated; no Core change or new simulator run
was made.  See `fast64/handoffs/FAST64_2_FORCED_STRESS_SEMANTIC_GATE.md`.
The FAST64 Goal is active again; FAST64.1 immutable R2 remains the first
formal-closeout priority whenever a fresh resource audit is safe.

## FAST64.1 immutable R2 recovery preparation (2026-09-08)

At this recovery checkpoint FAST64.1 was stage-gated by an execution-path
failure; no stage promotion and no R2 simulator launch had occurred.  Current
authority is `GOAL ACTIVE; FAST64.1 STAGE_GATE_PENDING`, rather than a global
Goal-blocked state.  Read-only `/proc` evidence resolves the
historical controller issue as
`ROOT_CAUSE_PROBABLE_ACTIVE_SCRIPT_MUTATION`: all live r1 Bash wrappers still
read fd `255` from the mutable worktree runner, whose SHA changed from the
launch snapshot's `6f078314…` to `14635253…`; the contaminated BICG OO parent
survived both observed epochs.  A second BICG OO@1048576 row has independently
produced the same two-epoch footprint and `line 74: d: command not found`.
The exact malformed continuation cannot be
reconstructed, so this is deliberately not labeled confirmed.

Future-only recovery is now prepared as a complete seven-row R2 wave, not a
one-row patch.  The v2 runner requires an SHA-verified, non-writable
`/tmp/fast64-runners/<sha>/` copy, one UUID, atomic namespace creation, and
immutable START/TERMINAL receipts.  Its validator requires the receipt chain
and a single-epoch proof calibrated on the clean NN rows.  A harmless
`/bin/true` test passed immutable binding, receipts, and duplicate namespace
rejection; it is not a scientific result.  The guarded dispatcher dynamically
admits only the fresh audited number of R2 workers; old r1 diagnostics are not
a scientific wait barrier.  The whole r1 qualification wave is
`SUPERSEDED_NONFORMAL_EXECUTION_PATH_AT_RISK`; all r1 collector output is
nonformal.  See
`fast64/handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.

The earlier R2 resource snapshot was `FAST64_1_R2_RESOURCE_WAIT_ACTIVE`, not
Goal blocked.  It has since been superseded by the fresh CPU-slot-wait
observation above; the dispatcher/collector/config/identity preparation and
independent FAST64.2 diagnostic work remain authorized.  Whenever a historical
job naturally exits, take a new resource audit and admit the highest-priority
safe R2 row without a wait-for-all barrier.

## FAST64.1 r1 execution-path contamination (2026-09-07)

This historical R1 checkpoint is nonpromotable; it does not describe the
current R2 execution state.  The
BICG OO@8192 r1 namespace has two observed simulator epochs in a single
exactly-once output directory, no `simulator_exit_status`, and a controller
anomaly (`line 74: d: command not found`).  Its prior epoch reached
47,231,655 cycles, but neither epoch is formal evidence.  The cgroup's
`oom_kill=12` is retained as host-pressure evidence only; causal attribution
has not been established.  All remaining live r1 and FAST64.2 processes are
preserved untouched.  A future-only atomic-namespace runner has passed a
harmless controller test; no formal recovery row has been launched.  See
`fast64/handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.

## FAST64 throughput-update checkpoint (2026-09-07)

FAST64 logical state remains **FAST64.1 ACTIVE**; no FAST64.1, FAST64.2, or
FAST64.3 PASS is claimed.  The seven formal-instrumented-Core r1 qualification
rows continue naturally and untouched.  The researcher-authorized scheduling
policy now separates strict `LOGICAL_STAGE_ACCEPTANCE` from provenance-bound
`PHYSICAL_PRECOMPUTED_ACQUISITION` (Framework `4144983b...`).

One high-cap BICG/IO lower-create stress diagnostic is live as
`PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE`; it uses the
formal `bbcbb5e...` Core and a source-coupled candidate-queue/PIB bound of one,
not a performance configuration.  NN/Base@8192 has naturally terminated and
strict-validated as `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` (6,985 cycles,
1,284,872 instructions, zero lower-cap-full and drained accounting).  It is
not yet an accepted FAST64.3 result.  Shared-host swap is exhausted and output
headroom is about 62 GiB, so the first controlled ramp stops pending a fresh
resource/throughput audit.  See
`fast64/handoffs/FAST64_PRECOMPUTED_ACQUISITION.md`.

Stage: M5.0BT exact trace capture and qualification — **RESOLVING_ISSUE
M5-0BT-011 (2MM SIM_HOST immutable-receipt capacity)**.

## C2P trace versus M5 ATAX host-throughput review (2026-09-07)

The requested non-invasive audit is recorded in
`m5/handoffs/M5_0BT_C2P_TRACE_HOST_THROUGHPUT_AUDIT.md`.  It establishes that
the historical C2P ATAX trace and the exact M5 NVBit trace are not the same
payload: kernel-1 ABI differs, C2P has `(16,1,1) x (256,1,1)` while M5 has
`(128,1,1) x (32,8,1)`, M5 kernel-1 has 8.95x C2P's dynamic instructions, and
the two-kernel M5 traceg set is 10.26x the C2P byte size.  C2P therefore
cannot be used as a formal M5 trace substitute, although it may later be an
explicitly nonformal host-diagnostic control.

The apparent 2,466-versus-about-280 simulated-cycles/s gap does not show a
nine-fold per-instruction host regression.  The available evidence decomposes
it into about 6.58x higher M5 simulated IPC/work per cycle and only about
1.34x lower host simulated-instruction throughput.  The live M5 process was
CPU-active with no sampled I/O wait or swap pressure; the shared legacy
observer settings and the independently equivalent A1 observer experiment
cannot explain the gap.  No active process, config, Core behavior, formal
result identity, or stage has changed.

## 2MM copyback storage admission (2026-09-06)

2MM has reached remote `ARCHIVE_PASS` with archive SHA-256
`59e918821bc54a772434acc70d2d439abefd8ccf696c055be2564b53d520863e`; this is
not yet a SIM_HOST receipt or formal result.  The fail-closed copyback gate
stopped before rsync because 36,313,600,000 local free bytes are below its
58,013,565,949-byte exact requirement (archive 3,416,630,277 + complete
bundle 50,301,968,376 + 4 GiB margin).  No payload was deleted, recaptured,
or unpacked.  Researcher-authorized archive-only rsync is now preserving the
compressed `.tar.zst` locally, but it is deliberately not a receipt: no
archive SHA, internal bundle validation, or `LOCAL_IMMUTABLE_PASS` is claimed.
`m5/handoffs/M5_0BT_2MM_STORAGE_ADMISSION_STOP.md` binds the evidence and
requires capacity provision followed by full transfer-only receipt resume;
M5.0BT remains ACTIVE.

### Background hold and rented-host disposition

At researcher direction, the live archive-only 2MM rsync and the repaired
ATAX Base/IO/OO replays continue naturally in the background while no new M5
stage work is started.  The compact handoff is
`m5/handoffs/M5_0BT_2MM_STORAGE_ADMISSION_STOP.md`.  The rented capture host
is **not yet safe to release** while this archive-only transfer is partial.
After its natural completion, a SHA-256 comparison of the compressed archive
to the recorded remote archive SHA is sufficient no-unpack proof that permits
capture-host release, while still leaving 2MM outside formal
`COPYBACK_SHA_PASS`/`LOCAL_IMMUTABLE_PASS`.  Its later formal receipt remains
gated on capacity plus internal-bundle and immutable-store validation.  This
is a provenance constraint; it does not imply an active GPU workload.

The archive-only transfer has now naturally completed.  Its local compressed
archive is exactly 3,416,630,277 bytes and direct SHA-256 matches the recorded
remote archive SHA:
`59e918821bc54a772434acc70d2d439abefd8ccf696c055be2564b53d520863e`.
`ARCHIVE_ONLY_COPYBACK_SHA_PASS` makes the rented V100 capture host safe to
release for storage purposes.  This no-unpack retention proof deliberately
does not promote 2MM to a formal immutable receipt or authorize a new M5
stage.

The researcher has authorized the interim eight-workload repaired-Core replay
batch (Paper-10 excluding `2mm` and `syrk`). Its exact scope, non-bypass ATAX
qualification gate, and dispatch order are frozen in
`m5/handoffs/M5_0BT_EIGHT_WORKLOAD_REPLAY_PLAN.md`. BICG and SpMV are retained
instead of duplicated; no new replay may bypass the live ATAX natural-terminal
parser/accounting gate.

A source audit has also confirmed a native `.traceg.xz` frontend route.  It is
an isolated `TEXT_TRACEG_XZ_DERIVED` storage candidate only, not an accepted
trace representation: byte-decompression, ordered-list, and same-bundle
Base/IO/OO differential proofs remain mandatory before formal use.  See
`m5/handoffs/M5_0BT_COMPRESSED_TRACE_STORAGE_CANDIDATE.md`.  Its first
no-write SpMV trace byte-round-trip PASS is evidence only, not a formal replay
or receipt claim.

## E1 local `sm_70` build preflight (2026-09-06)

BlackScholes has a reproducible, isolated CUDA-11.8 `sm_70` source/build/PTX
preflight with all legacy helper inputs hash-bound.  SIM_HOST has no visible
GPU, so it did not execute the source-defined `QA_PASSED` checker and has not
promoted the row beyond `SOURCE_READY`; `BUILD_READY` and
`TRACE_CAPTURE_READY` counts remain zero.  The exact candidate identities and
the mandatory real-V100 follow-up gates are recorded in
`m5/extended20/CUDA_SDK_E1_SOURCE_AUDIT.md` and
`m5/handoffs/M5_E1_V100_CAPTURE_READINESS.md`.  This is E1 preparation only;
it neither consumes V100 capture capacity nor changes the Paper-10 priority.
The canonical post-link artifact is an independently double-built,
byte-identical stripped ELF; the resolved nvcc local-symbol metadata issue is
recorded as `M5-E1-003`.

FastWalshTransform now has the same local two-build `sm_70` preflight under
its exact `-logK 11 -logD 19` source contract.  It remains `SOURCE_READY`
because no V100 output smoke or dynamic trace audit has run; E1 readiness
counts and the Paper-10 capture priority are unchanged.

VectorAdd and scalarProd have now passed the same two-build local `sm_70`
preflight with normalized ELF/PTX identities.  Neither has run a V100
source-defined output smoke or dynamic trace audit, so both remain
`SOURCE_READY`; the E1 readiness ledger remains unchanged.

Transpose, scan, and sortingNetworks have also completed their independent
two-build local `sm_70` preflights under their exact SDK 4.2 tree identities.
They remain `SOURCE_READY` pending V100 output smokes and dynamic trace audits;
the physical-capture queue and E1 readiness ledger remain unchanged.

convolutionSeparable has now completed the same isolated two-build CUDA-11.8
`sm_70` preflight from the frozen SDK 4.2 object.  Its normalized ELF and PTX
are byte-identical across both builds, but SIM_HOST did not run the real-V100
`--size 3072` L2-norm `QA_PASSED` checker or dynamic trace audit.  Its
constant-memory transfer path remains a runtime semantic gate, so it remains
`SOURCE_READY`; no readiness count, capture priority, or active V100 work is
changed.

Rodinia hotspot1 has independently passed an equivalent local CUDA-11.8
`sm_70` build/PTX reproducibility preflight from the clean 3.1 source tree.
It remains `INPUT_READY`, not `BUILD_READY`: no V100 source-defined checker,
input/runtime/launch freeze, or dynamic trace audit has run. The Paper-10
capture queue and all E1 exclusive readiness counts are unchanged.

Rodinia btree has also passed a two-build local CUDA-11.8 `sm_70` preflight,
including its two selected GPU-kernel PTX artifacts. A CUDA-11.8-compatible
compiler-driver wrapper replaces only the historical invalid quoted gencode
expansion; it changes no source, launch, or runtime semantics. btree remains
`INPUT_READY`, not `BUILD_READY`, pending its V100 checker and dynamic trace
audit; Paper-10 capture priority and readiness counts are unchanged.

Rodinia lud likewise has a two-build local CUDA-11.8 `sm_70` preflight,
preserving its source-defined `-O3 -use_fast_math` build mode and three kernel
PTX entries. It remains `INPUT_READY`, not `BUILD_READY`: the V100 verifier,
runtime/input/launch freeze, and dynamic trace audit have not run. Paper-10
capture priority and readiness counts remain unchanged.

Rodinia dwt2d has also completed a two-build local CUDA-11.8 `sm_70` preflight
with a reproducible eight-unit PTX manifest. It remains `INPUT_READY`, not
`BUILD_READY`, pending source-defined output/reference checking and dynamic
trace audit; Paper-10 capture priority and readiness counts are unchanged.

Rodinia gaussian has likewise completed a two-build local CUDA-11.8 `sm_70`
preflight while preserving its source-defined workgroup constants. It remains
`SOURCE_READY`, not `BUILD_READY`, pending a selected input/checker, V100
smoke, and dynamic trace audit; Paper-10 capture priority is unchanged.

Rodinia cfd_097k has completed an independently repeated local CUDA-11.8
`sm_70` build/PTX preflight using only the exact frozen tree's legacy
host-timer helper headers.  This source-bound dependency recovery changes no
workload source or runtime semantics.  Because CFD uses constant-memory setup,
it remains `INPUT_READY/RUNTIME_AUDIT_CONSTANT`, not `BUILD_READY`: a real
V100 checker, frozen launch/input contract, and dynamic trace-ordering audit
are still required.  Paper-10 capture priority and all readiness counts are
unchanged.

## Live audit update (2026-09-06)

The natural-terminal BICG stats-light A0/A1 comparisons and the required
independent same-placement IO confirmation are complete. Base, repaired
PAPER_IO, and repaired PAPER_OO strict-parse and match exactly in every
parser-visible scientific field, including final cycles/instructions,
DTC lifecycle/accounting, and parser-visible traffic. The same-placement
confirmation again found zero differing metrics and natural zero drain.
A1 (`gpgpu_runtime_stat=500000`, observer-overlay SHA
`2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`) is now
adopted for **future, not-yet-launched** formal triplets only. Existing valid
A0 rows are neither rerun nor relabelled, and no future triplet may mix A0/A1.
See `m5/handoffs/M5_STATS_LIGHT_A1_TERMINAL_EQUIVALENCE.md`.

The repaired BICG Base replay has now naturally terminated (exit zero), strict
parsed, and reclosed the same-bundle repaired-Core T2 triplet with IO/OO.
`review_packs/M5_0BT_T2_BICG/` is now bound to Core `15cfa76e...`; the
pre-repair T2 remains diagnostic only.  The ATAX Base/IO/OO recovery triplet
remains live, so the lower-create repair gate is not yet PASS; repaired MVT
replacement and repaired GESUMMV T3 remain correctly gated by its required
natural-terminal/parser/drain closure.

The source-script capture route has been recovered and read non-invasively.
SpMV is `ARCHIVE_PASS`, has copyback SHA and local immutable validation PASS,
and is bound to exact source/input/tracer identity in
`m5/handoffs/M5_0BT_SPMV_CAPTURE_CLOSEOUT.md`.  2MM has completed its
capture/postprocess phase and is currently controller `ARCHIVE_PENDING`; it
has no archive/transfer/result claim yet. No production capture was restarted
or duplicated during the reachability recovery.

The newly immutable SpMV bundle has entered the repaired-Core SIM_HOST pool as
three isolated `PRECOMPUTED_PENDING_STAGE_ACCEPTANCE` Base/IO/OO rows.  All
three have loaded the first immutable `.traceg` through the trace frontend,
with empty stderr; no formal-result claim is made before their own natural
terminal/parser/accounting closure.

## Current capture-storage authority (2026-09-06)

SYR2K has reached remote ARCHIVE_PASS with an exact 57,694,970,930-byte
working bundle, exceeding the old 55,353,177,980-byte 2DConv-based aggregate
projection. Future capture uses the researcher-authorized serial-streaming
admission floor of 61,516,599,357 bytes: the maximum measured complete SYR2K
bundle + archive + measurable scratch footprint. The old ten-bundle/twofold
multiplier is superseded because proof-bound streaming offload is now required.
SYR2K now has copyback SHA and local immutable validation PASS: its remote
archive SHA, local resumed archive SHA, unpacked internal sums and capture
bundle have closed under receipt
`6a6b590dc7d05a10d85ab30b37c6350092aba981c65be82249c6374e3e825513`.
The proof-bound remote working-bundle eviction and fresh live gate have since
passed; only the redundant remote SYR2K working bundle was eligible, while its
archive/provenance remain retained. The ordered SpMV -> 2MM queue has been
restarted, but no SpMV capture/archive/transfer/result is claimed yet. 2MM is
HEAVY_SIZE_UNKNOWN and may start only under the recalibrated gate. See
docs/dtc_l1/m5/handoffs/M5_0BT_SYR2K_HEAVY_STORAGE_RECALIBRATION.md.

Status: M5.0BT T1, BICG/2DConv storage admission, immutable-store copybacks,
and T2 BICG same-bundle Base/IO/OO replay qualification PASS.  T3 GESUMMV
same-bundle Base/IO/OO formal replay is ACTIVE; `CAPTURE_AND_REPLAY_PIPELINED`.
**New Core recovery active:** four precomputed ATAX/MVT IO/OO rows aborted
at the bounded lower-create queue assertion.  Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` replaces that post-allocation
abort with pre-allocation retriable backpressure and retains all correctness
assertions.  Exact-bundle ATAX IO/OO recovery replays are active under the
new runtime; neither they nor any old-Core row is a formal result yet.
The existing BICG T2 and live GESUMMV T3 replays use pre-repair Core
`12097864...`; preserve them to natural termination, but treat them as
diagnostic/mechanism anchors.  Same-bundle triplets under `15cfa76e...` are
required before a repaired-identity T2/T3 formal acceptance claim.

## Live scheduling update

### Concurrent three-track checkpoint

- **Track A — T3 (pre-repair diagnostic):** GESUMMV Base/IO/OO run as
  independent sessions on the
  immutable `d8cf9b57...` bundle under the frozen 80-SM/cap-10240/ratio-zero
  identities.  The latest non-invasive counter sample was Base
  `2,446,000` cycles / `5,539,040` instructions, IO `1,809,000` /
  `24,494,688`, and OO `1,864,000` / `22,761,472`; all three processes were
  CPU-active with no fatal/assert/deadlock signature (the only `deadlock`
  text is the printed enabled-config option).  They must naturally terminate.
  Because their Core predates the lower-create-queue repair, they cannot close
  repaired-identity T3 and a new-Core same-bundle replacement triplet remains
  required.
- **Track B — V100 capture:** ATAX is `ARCHIVE_PASS` remotely and locally
  transfer-verified: archive SHA-256
  `4db328affd8a81d444bca1bc034110e1e51458fbce6ab901078a101c6beadff3`,
  internal sums PASS, controller `valid_bundle()` PASS, and checker PASS with
  zero mismatches.  It is a T4-eligible payload, not a formal performance
  result.  GEMVER has remote checker/archival PASS.  MVT has now completed
  checker/archive/copyback: archive SHA-256
  `6c537caf1e110c3804bdc943211078565580f88d9ed85ac8dfa12d685964f270`,
  bundle ID `8b96abe81eed02a614014401cb074ff9d57abd3dc6ba72260167050679ca4f3a`,
  internal sums PASS, and `valid_bundle()` PASS at preserved local root
  `/workspace/m5-trace-immutable/mvt/mvt/mvt`.  SYRK has since reached
  `ARCHIVE_PASS` with bundle
  `66957eacdb8435c12c097631460450923adf9ed39bf8bfe37464cdf868c9a09b` and
  archive SHA-256
  `b82e9ef0310778f8e3493ca555532a636a08f84e466d9e733ebea53a11b3b6a3`;
  SIM_HOST copyback is active but local immutable validation is not yet a
  claim.  The subsequent SYR2K launch was refused before capture by the
  controller's fail-closed heterogeneous-storage projection gate
  (`RuntimeError: unsafe projected heterogeneous trace storage`): no SYR2K
  state, trace, or capture process was created.  Researcher-authorized,
  provenance-preserving R1/R2 reclamation then removed only regenerable
  capture scratch and one checker-failed, non-candidate GESUMMV raw attempt;
  its compact logs/provenance were retained.  The unchanged gate subsequently
  passed (`55,478,362,112` free bytes versus `55,353,177,980` projected), and
  the single SYR2K controller resumed under the capture lock.  While SYR2K
  was actively capturing, the proof-bound R3 controller operation offloaded
  only the redundant remote ATAX working bundle (5,806,756,882 bytes); its
  remote archive and all verified SIM_HOST artifacts remain preserved.  The
  post-R3 unchanged gate passed with 59,432,751,104 free bytes.  See
  `m5/handoffs/M5_0BT_AUTODL_SPACE_RECLAMATION.md`.  None of these capture
  bundles is a formal result.  As SYR2K's live trace later consumed the
  start-gate margin, R4 used the same proof-bound controller action for MVT:
  only its redundant 5,777,441,032-byte remote working bundle was removed,
  after remote/local archive SHA and local immutable manifest validation
  matched.  Its remote archive and SIM_HOST immutable payload remain intact;
  the post-R4 unchanged gate passed with 59,907,649,536 free bytes.  SYR2K
  remained active throughout.  R5 then proof-bound-offloaded only GEMVER's
  redundant 2,647,569,402-byte remote working bundle after the same archive
  and local immutable checks; its archive and local payload remain preserved,
  and the unmodified gate passed with 59,551,346,688 free bytes.
- **Track C — SIM_HOST statistics-light A/B:** the initial BICG
  same-trace/same-binary/80-SM/cap-10240/PAPER_BASE cutoff round established
  that `gpgpu_max_cycle=2000000` is not a valid DTC observation boundary: it
  bypasses normal drain and correctly fails the terminal lifecycle assertion.
  Those outputs remain diagnostic-only.  A separately isolated natural-
  terminal A0--A3 round is active.  A0 is current observer
  settings; A1 sparse runtime CSV; A2 additionally suppresses the final PTX
  line report; A3 additionally disables generic memlatency observer stats.
  This does not alter a formal run or registry.  See
  `m5/handoffs/M5_SIM_HOST_STATS_LIGHT_AUDIT.md`; no candidate is adopted
  until terminal counter equivalence and a controlled confirmation pass.

- **Pipelined returned-trace acquisition:** researcher authorization permits
  independent replay acquisition before T3/M5.0BT logical PASS.  The fully
  validated ATAX, GEMVER and MVT immutable payloads each have a Base/IO/OO
  replay on the unchanged frozen formal configuration, recorded as
  `PRECOMPUTED_PENDING_STAGE_ACCEPTANCE` in
  `m5/handoffs/M5_0BT_PRECOMPUTED_REPLAY_QUEUE.md`.  These live rows are not
  a stage result and must close all terminal/parser/accounting gates before
  later exact-identity reuse.

- **Lower-create queue recovery:** the frozen 80-SM/cap-10240 pool exposed
  the same source-reachable IO/OO assertion for ATAX and MVT.  The failed
  evidence is preserved, excluded from the registry, and documented in
  `implementation/M5_PRECOMPUTED_LOWER_CREATE_QUEUE_FAILURE.md`.  The Core
  repair exports explicit queue-full stall counters, passes the three DTC
  CTests in an isolated Release build, and has an isolated trace frontend
  runtime.  ATAX IO (PID `1045897`) and OO (PID `1045896`) now replay the same
  immutable bundle/config in a separate recovery namespace.  At 101 s both
  exceeded their old 83.81 s / 84.96 s abort window with empty stderr and no
  assertion/fatal/deadlock/error signature.  They must still close natural-
  terminal/parser/accounting gates before any post-repair formal reuse; MVT
  remains queued behind that evidence.  This is a HARD recovery gate, not a
  stage advance.

- **Repaired-identity replay pool:** isolated runtimes built from Core
  `15cfa76e...` now run ATAX Base/IO/OO and BICG Base/IO/OO on their existing
  immutable bundles/configs.  ATAX uses Framework `2bb015a8...`; BICG uses
  Framework `dc7836c4...`; each triplet is internally source-identical.  The
  BICG triplet is the post-repair T2 replacement, not a duplicate formal result.  The
  dynamically calibrated pool has 18 live simulator workers, including the
  four stats-light diagnostics; MemAvailable remains about 101 GiB with zero
  swap I/O, so further dispatch is frozen pending a natural exit or fresh
  calibration.  See `m5/handoffs/M5_REPAIRED_CORE_REPLAY_POOL.md`.

- BICG Base remains a verified trace-driven replay, not a PTX/execution-driven
  payload: its live argv uses immutable BICG `kernelslist.g`, loads both
  ordered `.traceg` invocations through the trace frontend, and has no trace
  corruption/fatal/assert/deadlock/output-mismatch signature. Its immutable
  bundle ID is `ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33`.
- A 90-second read-only sample recorded `33,182,550 -> 33,316,550` current
  kernel cycles and `54,363,616 -> 54,570,624` instructions: about 1,489
  cycles/s and 2,300 instructions/s. Classification:
  `TRACE_REPLAY_HEALTHY_PROGRESSING`. Base subsequently naturally terminated
  and strict-parsed at `50,303,549` cycles / `158,601,216` instructions; the
  full same-bundle BICG Base/IO/OO qualification is now T2 PASS. Its review
  pack is `review_packs/M5_0BT_T2_BICG/`; T3 is the next logical replay gate.
- Physical V100 capture now pipelines independently. The first GESUMMV
  (`gesu`) attempt is preserved `RETRY_READY`: its checker found 1,964
  mismatches caused by the pinned CUDA source copying uninitialized host
  `tmp`/`y` into additive device accumulators. A source-copy-only repair is
  hash-constrained to those two zero initializations and records both source
  hashes/replacements in capture provenance; the frozen source and failed raw
  attempt are untouched. Its corrected replacement capture now has checker,
  immutable-bundle/archive, copyback-SHA and local bundle-revalidation PASS;
  it is a T3 payload, not yet a formal result. Framework
  `14be71c7968f0fb5bc1e021cf40eda41d8314171` corrects the controller's
  heavy-pilot admission formula and passes its no-GPU regressions. This is a
  capture-controller repair only; it changes no trace bundle, replay config,
  Core behavior, or formal result.
- See `m5/handoffs/M5_0BT_CAPTURE_REPLAY_PIPELINE.md`. Capture ahead of replay
  is a scheduling admission only; M5.0C remains prohibited until full M5.0BT
  acceptance.

## Current authoritative state

### Throughput checkpoint (2026-09-06)

- Researcher-authorized worker recovery preserved and then gracefully retired
  stats-light A2/A3 and the old-Core GESUMMV Base/IO/OO diagnostics.  The
  exact preserved namespaces, pre-signal evidence, classifications and PGIDs
  are recorded in `m5/handoffs/M5_SIM_HOST_STATS_LIGHT_AUDIT.md` and
  `m5/handoffs/M5_REPAIRED_CORE_REPLAY_POOL.md`.  No repaired-Core formal
  candidate was signaled, no raw evidence was deleted, and no `SIGKILL` was
  required.
- The real container CPU boundary is a 384-core cgroup quota with cpuset
  `0-511`, not an 18-core allocation.  Eighteen was a conservative shared-host
  scheduling limit.  After retirement, BICG repaired PAPER_IO/PAPER_OO A1
  natural-terminal observer-only confirmations started on dedicated CPUs 46
  and 47 (`1512229`, `1512240`); they retain the immutable BICG trace, Core
  `15cfa76e...`, 80-SM/cap10240/ratio-zero model and differ only by runtime
  statistics cadence.  They are not adoption/formal results pending full
  terminal equivalence.
- ATAX repaired Base/IO/OO remain live and have only exceeded the historical
  abort window; they have not completed the HARD terminal/parser/drain/lower
  accounting gate.  Consequently MVT IO/OO and repaired GESUMMV T3 are ready
  for priority dispatch but remain correctly gated, rather than being launched
  under an unqualified repaired runtime.

### Capture-storage recovery R6 (2026-09-06)

- SYRK reached archive/copyback/local-immutable PASS and was then reclaimed
  only through the proof-bound controller path.  `bundles/syrk` (27,998,390,213
  bytes) was removed; its remote archive, local immutable payload and evidence
  were preserved.  Free space increased from the last pre-controller observed
  54,673,100,800 bytes to 82,369,568,768 bytes while SYR2K continued capture.
  See `m5/handoffs/M5_0BT_AUTODL_SPACE_RECLAMATION.md` and remote
  `reclamation/R6_syrk_offload_evict.json`.
- The AutoDL control plane is again readable through the live capture-host
  route.  SYR2K is in its natural post-GPU trace-processing phase:
  application checker PASS (zero mismatches), raw trace present, and the
  controller remains live while its CPU postprocessor runs.  Its state is
  still `CAPTURING`, so neither `ARCHIVE_PASS` nor copyback is claimed.
- The next exact SpMV payload's canonical matrix/vector/reference identities
  and clean wrapper `de9cf429...` / tree `5b8b3a8...` remain verified.  Both
  SIM_HOST source bundles were copied to an isolated AutoDL staging area with
  SHA-256 and complete-history bundle verification; a clean detached
  `parboil@4e0fc548...` / tree `0bc8944...` checkout now occupies the source
  path consumed by the existing queue supervisor.  This replaces the
  prolonged non-candidate public clone without changing any capture artifact.
  The supervisor is now fail-closed only on SYR2K `ARCHIVE_PASS`, storage, and
  the capture lock before starting SpMV, then applies the same ordering to
  2MM.  See `m5/handoffs/M5_0BT_SPMV_SOURCE_TRANSFER_READY.md`.
- 2MM CPU-side preparation and isolated AutoDL source-tar transfer are both
  verified: clean `polybenchGpu@5584aaa7...` source/header hashes,
  deterministic tar identity, sm70 build, source checker and dimensions are
  frozen in `m5/handoffs/M5_0BT_2MM_CAPTURE_READY.md`.  It remains `PENDING`
  and may start only after SpMV reaches its safe archive state and the normal
  lock/storage gates pass.

### Live throughput checkpoint (2026-09-06T12:19+08:00)

- The repaired-Core BICG PAPER_OO A0 replay naturally ended with exit status
  zero and strict parser/drain/accounting PASS in its isolated output
  namespace.  It records 8,764,792 cycles / 158,601,216 instructions, lower
  create/issue/response `17,827,090/17,827,090/17,827,090`, dependencies
  `18,350,080/18,350,080`, and final OO PIB/inflight/active-ref/lower state
  all zero.  It is only a `POST_REPAIR_T2_REPLAY_CANDIDATE`: repaired BICG
  Base/IO and the required IO/OO A1 equivalence confirmations are still live,
  so no T2 re-close, stats-light adoption, or formal registry update occurs.
- The repaired-Core BICG PAPER_IO A0 member has now also naturally ended and
  strict-parsed: 9,324,397 cycles / 158,601,216 instructions, lower
  create/issue/response `17,823,985/17,823,985/17,823,985`, dependencies
  `18,350,080/18,350,080`, and final IO inflight/PIB/lower state all zero.
  No assertion, fatal, output mismatch, or non-config deadlock text was
  observed.  This leaves only repaired BICG Base A0 before same-bundle T2
  triplet reconciliation; the IO/OO A1 stats-light confirmations remain live.
- **Current-pool correction (2026-09-06T12:33+08:00):** after the BICG IO A0
  terminal transition, 13 (not 14) isolated M5 simulator processes remain
  live.  The repaired BICG IO/OO A0 rows are recorded in the replay-job
  manifest as `POST_REPAIR_T2_REPLAY_CANDIDATE`; they are not registered
  formal results and still await Base A0 plus same-mode A1 equivalence.
- At the 12:19 historical snapshot, fourteen isolated M5 simulator processes
  remained active and each continued
  to accrue near-one-core CPU time.  The dynamic limit remains `N_safe=18`;
  the unfilled capacity is intentionally protected until repaired ATAX
  Base/IO/OO close their natural-terminal/parser/drain gate, after which MVT
  IO/OO and repaired GESUMMV receive priority.  The container has cpuset
  `0-511` and a non-throttling 384-core `cpu.max` quota, but the shared host
  load is about 440 and does not support increasing concurrency from topology
  alone.
- Two non-invasive V100 SSH probes were refused during this checkpoint.  No
  remote process, queue, archive, or state file was touched, and this is not
  classified as a capture failure.  Continue local replays and resume the
  existing fail-closed `SYR2K -> SpMV -> 2MM` capture pipeline only after the
  host is reachable and its retained controller state can be read.

### Extended E1 offline provenance progress (2026-09-06)

- The six selected Parboil input sets were byte-hash and Git-blob revalidated
  in clean `parboil@4e0fc548...`; the six selected checker identities remain
  source-pinned.  The Python-3 source-predicate adapter recompiled and passed
  all six accepted/mismatch fixtures.  This closes local input/checker drift
  evidence only: CUDA builds, PTX, generated output references/smokes, payload
  eligibility and all Rodinia input recovery remain pending.  No Extended
  simulation, trace capture, result registration, or E2 launch occurred.
- The eight selected CUDA SDK 4.2 source files were independently rehashed
  straight from Git commit `b059fdae...`; all match the recorded E1 source
  identities.  This is source-only provenance confirmation: executable/PTX
  artifact revalidation, deterministic runtime I/O, source-defined smoke and
  M5.2 anchor recheck remain required.
- A conservative static source audit now classifies the six Parboil rows
  before any V100 work: BFS (atomics/textures/global barrier), CUTCP
  (stream/constant memory), Histo (atomics), MRI-Q (constant memory), and
  SAD (textures) require workload-local runtime semantic audits; Stencil is a
  static trace candidate only.  None is yet `TRACE_CAPTURE_READY`, no feature
  is presumed unsupported, and the per-row readiness table remains the
  capture scheduling authority.  See
  `m5/extended20/M5_E1_PARBOIL_STATIC_TRACE_FEATURE_AUDIT.md` and
  `m5/handoffs/M5_E1_V100_CAPTURE_READINESS.md`.
- The selected Rodinia 3.1 CUDA source scan likewise identifies CFD's
  constant-memory transfer path for a runtime audit; BTree, DWT2D, Gaussian,
  Hotspot1 and LUD are static candidates only.  Their missing deterministic
  inputs/checkers and all clean V100/sm70 builds still prohibit capture.  See
  `m5/extended20/M5_E1_RODINIA_STATIC_TRACE_FEATURE_AUDIT.md`.
- The CUDA SDK 4.2 static screen identifies convolutionSeparable's
  constant-memory transfer path; the other seven selected rows are static
  candidates only.  All eight already have recorded local CUDA-11.8/sm70
  build/PTX preflights, but no SDK row can capture before its own real-V100
  output smoke/checker, input/launch/runtime freeze and dynamic contract.  See
  `m5/extended20/M5_E1_CUDA_SDK_STATIC_TRACE_FEATURE_AUDIT.md`.
- The source-recorded Rodinia 3.1 data archive is now archive-hashed and only
  the approved input members have been materialized in an isolated local E1
  namespace.  CFD, BTree, DWT2D and Hotspot now have exact launcher-input
  hashes; LUD's source-generated `-s 256` contract is distinguished from a
  data file.  Gaussian has several source-recorded candidates and remains
  deliberately unfrozen.  No V100 capture, build, trace or formal result was
  started.  See `extended20/RODINIA_PARBOIL_E1_SOURCE_AUDIT.md`.

- One persistent Goal: docs/dtc_l1/m5/M5_TRACE_TO_FINAL_SINGLE_GOAL_CONTRACT.md.
- M5.0BT is active and gates M5.0C. No M5.0C, Extended E2, graphics work, or
  capture-host rental/start is authorized by this report.
- Formal platform is 80 SM, global lower cap 10240 (128 credits/SM), and
  ratio-zero. The 80-SM/cap-256 combination is historical diagnostic-only.
- M5.0BT has a workload-specific, source-pinned CUDA-11.8/sm70 capture
  controller, immutable bundle validation, external archive/transfer states,
  non-bypassable BICG-based storage admission, and SIM_HOST orchestrator.
- The two remote checkouts are non-interchangeable: current M5 control checkout
  runs the command; detached 0db04452ec1c47630e4b08002067d82c6811e243
  supplies tracer sources only.
- The provisioned capture host passed V100/CC7.0, CUDA 11.8, toolchain,
  writable-data-volume and pinned-source preflight. M5-0BT-001 was repaired
  before CUDA build; M5-0BT-002 then found an unrelated root-Makefile legacy
  tool after the required trace tool/postprocessor compiled. Its scoped-build
  repair and regression contract now pass. Retry-4 completed that build but
  exposed M5-0BT-003: the host identity probe used incorrect CUDA Runtime UUID
  APIs. The compact Driver-API UUID adapter passed isolated CUDA-11.8/V100
  revalidation (properties, Driver UUID and CC 7.0 agree with `nvidia-smi`).
  No application, raw trace, immutable bundle or formal result has been
  created. Retry-5 reached the BICG CUDA build and exposed M5-0BT-004: its
  selected-workload loop propagated a false final predicate as status 1 after
  a successful `nvcc` build. The explicit-success repair passed an exact V100
  BICG build retest. Frozen source, CUDA 11.8 and sm70 build contract are
  unchanged; each fresh build's executable SHA is captured as provenance.
  Retry-6 then loaded NVBit on V100 but found the installed CUDA-11.8
  `nvdisasm` absent from the application PATH (M5-0BT-005). Retry-7's PATH
  repair passed: the BICG checker passed and full raw traces were captured.
  Its postprocess exposed M5-0BT-006; retry-8 passed that legacy-layout
  adapter, application checker, raw capture and `.traceg` postprocess. It then
  exposed M5-0BT-007; its CSV repair passed on resume. Strict mapping then
  exposed M5-0BT-008; its line-preserving repair also passed. Finalization
  reached record construction and exposed M5-0BT-009: it had not materialized
  the validated manifest files before hashing them. Its write-before-hash
  repair passed: retry-8 is now an immutable, archived BICG T1 bundle. See
  `m5/handoffs/M5_0BT_BICG_T1_REVIEW.md`. The archive was SHA-verified after
  copyback, unpacked once into the immutable replay store, and internally
  revalidated against its bundle sums. The BICG admission projects
  47,591,571,552 bytes against 104,537,268,224 measured free bytes, but is
  provisional because BICG's two small-grid invocations do not bound 2DConv.
  The required exact 2DConv 65,536-CTA heavy pilot now passes its hardware
  checker, archive/copyback SHA chain and internal immutable-store sum check.
  Its conservative ten-workload/twofold-reserve projection is 55,353,177,980
  bytes below 101,566,291,968 measured free bytes, admitting the remaining
  sequential Paper queue. See `m5/handoffs/M5_0BT_BICG_ADMISSION_COPYBACK.md`
  and `m5/handoffs/M5_0BT_2DCONV_HEAVY_ADMISSION.md`.

## Required next action after a V100 host is supplied

Complete natural-terminal GESUMMV T3 qualification while the exact Paper
capture queue continues independently.  Then obtain/qualify the remaining
Paper trace bundles.  No M5.0C transition is authorized.

## HISTORICAL / SUPERSEDED — DO NOT EXECUTE

The prior execution-driven M5.0B cap-256 workload campaigns, their former
natural-terminal wait, and their five terminated recovery jobs are preserved
only as source/provenance and mechanism-validation evidence. They are not
formal performance inputs and impose no active transition condition.
