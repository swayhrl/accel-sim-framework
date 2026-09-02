# B07 recovery evidence

Status: `R07.1_R07.5_COMPLETE_R07.6_PENDING`

This document records bounded recovery evidence only.  It does not mark M1 as
passed and does not authorize M2.

## Source anchors

| Role | Core SHA | Framework SHA |
| --- | --- | --- |
| pre-fix semantic baseline | `581fff76cf1dabbf1b2b9fe709a0f2142ab0d8e7` | `9c2e10a191991148e447b1b170bec0491f25e839` |
| post-fix recovery | `06aa534aab516578cb481e74bf006927a1828d58` | this evidence commit pending |
| frozen clean upstream | `91880c53383d5a6a6742bfb1be2c5f34e39c7871` | n/a |

The post-fix Core change is limited to pairing the existing true completion
event in `ldst_unit::L1_latency_queue_cycle()` with the idempotent
`dtc_l1_retire()`, plus a default-off bounded debug trace and a drain
invariant.  It does not alter cache probe, fill, MSHR, NoC, or DRAM semantics.

## R07.1: bounded pre-fix localization — PASS

The debug event limit is default `0`; these diagnostics used a finite limit of
`256`.  The deterministic L1-hit microbenchmark first issued a miss, received
its fill, and then repeatedly accessed the same line as an L1 hit.  Its
pre-fix log records:

- `L1_FILL uid=6` at cycle `5204`;
- true L1-hit completions for UIDs `11,16,21,26,31,36,41,46`;
- each `HIT_TRUE_COMPLETE_NO_RETIRE` event still had `tracked=1`;
- the ninth candidate UID `51` was repeatedly rejected with
  `PIB_BLOCK live_count=8`.

This confirms the source finding: the L1-hit path reached
`warp_inst_complete()` but did not remove the tracked UID.  The run deadlocked
after the PIB filled; it is `PRE_FIX` diagnostic evidence, not a M1 failure
after the authorized recovery started.

The original B07 stress configuration also reached `live_count=8` and then
repeated `PIB_BLOCK` while the first same-line miss was pending.  That trace
establishes the direct B07 no-progress context.  The source-supported config
uses `-gpgpu_cache:dl1 ... A:1:1,...` and
`-gpgpu_dtc_l1_mshr_entries 1`; no source-only MSHR override is used.

## R07.2/R07.3: minimal fix and permanent coverage — PASS

`shader.cc` now performs, in order, at the existing L1-hit true completion
point:

1. `warp_inst_complete(mf_next->get_inst())`;
2. `dtc_l1_retire(mf_next->get_inst())`.

`dtc_l1_retire()` removes the UID from the live set first and is therefore
idempotent for any completion path that reports the same source completion
more than once.  At final Paper-Base statistic emission the aggregate
invariant asserts `pib_admits == pib_retires` and `pib_occupancy == 0`.
`paper_frontend::assert_drained()` and the directed M1 CTest cover the same
drain condition.

All `ldst_unit` `warp_inst_complete` call sites were audited:

| Completion path | DTC retirement |
| --- | --- |
| L1-latency queue load `HIT` | paired by this recovery |
| `writeback_complete()` | already paired |
| load dispatch when no pending requests remain | already paired |
| sync/arrive completion path | already paired; non-load paths remain outside the M1 Paper-Base load test scope |

The post-fix L1-hit run records `RETIRE` followed by
`HIT_TRUE_COMPLETE_RETIRED tracked=0` for every sampled hit.  It completes
with `DTC_L1_pib_admits = 65`, `DTC_L1_pib_retires = 65`,
`DTC_L1_pib_occupancy = 0`, and application self-check `PASS`.

## R07.4: controlled B07 recovery — PASS

Workload identity:

- executable SHA256: `55a5a5b9f89cccf0f018316450c3a4b1294e6d4fd8db0aa3657d8410325036f8`;
- PTX SHA256: `02e1e8f1fe6c1d0aed82b65ed9abd955fe57fed76a4766b360f6deb747bef569`.

| Case | Effective conventional MSHR | Result |
| --- | --- | --- |
| stress | entries `1`, max-merge `1`; config SHA256 `752e7ff2770d61a8f0b03643005b7d707da3a45ef572240a2f6dcfc602b15a97` | `MSHR_MERGE_ENRTY_FAIL=166`; first fill at cycle 5256; retries subsequently hit/retire; 33 admits/33 retires/0 live; 5,525 cycles; application PASS; no watchdog |
| less-pathological | entries `1`, max-merge `2`; config SHA256 `efce165cfac30d32c99f76981cb7482e190d7499eb45ae068632a63e94ab5dab` | `MSHR_MERGE_ENRTY_FAIL=165`; 33/33/0 PIB closure; 5,525 cycles; application PASS; no watchdog |

## R07.5: frozen clean-upstream differential — PASS

Frozen Core `91880c53383d5a6a6742bfb1be2c5f34e39c7871` was run in native
LEGACY behavior with the identical B07 workload and `A:1:1` conventional L1
geometry (config SHA256
`800f62d62a9255738d2648b112dacd69e39bbb9ff14308fd4f39b517ffc42293`).
It completed with 5,500 cycles, 8,196 dynamic instructions, 33 L1D accesses,
2 L1D misses, one L2 global-read access, zero DRAM reads, and
`MSHR_MERGE_ENRTY_FAIL=166`.  The application self-check passed and no
watchdog fired.  Fixed Paper Base preserves the same conventional merge-full
count and completion behavior; its additional 25 cycles are Paper-Base
front-end timing, not an MSHR semantic change.

## Raw-log index

Raw logs are intentionally outside version control.

| Classification | External log path | SHA256 |
| --- | --- | --- |
| `PRE_FIX` B07 | `/tmp/dtc-l1-b07-prefix-5Iqwvu/run.log` | `b4dcc1bb8a8ac537594869862a62597bb1d06639415763beec2c84f65934146f` |
| `PRE_FIX` hit localization | `/tmp/dtc-l1-hit-prefix-oGtVX7/run.log` | `a31500129c9b92ca358db4fde0c227894d529a9e4bd8f5f40f5ea078a3853461` |
| `DIAGNOSTIC` fixed hit regression | `/tmp/dtc-l1-hit-prefix-oGtVX7/run-postfix.log` | `1e7a3774eb0c416b6104a7235767a5a8ef24d8a1a1d7f7b7c067fa95cbebd661` |
| `DIAGNOSTIC` B07 max-merge 1 | `/tmp/dtc-l1-b07-prefix-5Iqwvu/run-postfix.log` | `fce3d9edc1c078c49a528d151de85f4dd824b6a3cf15de68110a000452ffaf49` |
| `DIAGNOSTIC` B07 max-merge 2 | `/tmp/dtc-l1-b07-merge2-SK0d6v/run.log` | `699085960f0f8330dd764d51ecfee5151e225e039e6c75afd9df10e388fe078b` |
| `FORMAL_VALIDATION` frozen clean B07 | `/tmp/dtc-l1-b07-clean-v5uccW/run.log` | `abf928128d658a789af2632720c5741505006d083acf6471f23cd5f7ae3a25ec` |

## Next gate

R07.6 remains required: rerun every M1 HARD gate, LEGACY exact differential
set, counter/parser closure, release build, and clean-worktree checks.  Do
not create `review_packs/M1_FOUNDATION/` or begin M2 until that work passes.
