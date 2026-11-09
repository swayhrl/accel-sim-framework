# CPU qualification and independent Gate review

Review identity: `/root/cpu_review`, a read-only CPU reviewer assigned by the sole 174-DTC Main. Review date: 2026-11-09. I did not edit the candidate source, register a scientific request or UUID, dispatch a model, or use a GPU.

## Fixed identity and reviewed paths

| Item | Fixed identity |
| --- | --- |
| Goal contract | `swayhrl/accel-sim-framework` `32cbe43f6975ff6a11cfd1210f88026771656b48` |
| Baseline core | `9eedb3131937748f0492fa83aad37d3691118d70` |
| Isolated candidate core | `/root/data/dtc_finite_service_completion_v1_20261109/core`, clean commit `9a0de9b9f97144f481b3e3637e329ebab01acb74` |
| Framework source | clean commit `02775fd795cde5aae1480d81cee6eb481d0a08f4` |
| Independent CPU build | `/root/data/dtc_finite_service_completion_v1_20261109/cpu_review_build` |
| Frozen science build receipt | `evidence/BUILD_RECEIPT.json`, SHA256 `4f3b3b768157a2210844a2e3e3a524d2e55b4b933a41a0f775429ad91e0fbcb4` |
| Frozen framework binary | `accel-sim.out`, SHA256 `a9ec6f231d9491690eb913d1cb69d7d2dae0f769f8854efc4df0512b5f1fd00c` |
| Frozen core library | `libcudart.so`, SHA256 `43b3dc2f3e04d577e6c682f632691aca637b2670aee52c18b809f4d4c4e64860` |

Before the candidate was committed, I verified `git diff --check` and the six-file diff SHA256 `7af7e4afadb16cf5b377a77690225572a264de858f5bdbfc0cc401675f949969`. The committed tree contains that candidate. My separately built `libcudart.so` had SHA256 `675ca38ad22437608eab48ad939f11d739db4f1f2368dd7a075461d92880915a`; it is a different build artifact and is **not** the frozen science library above.

## Gate A: candidate and counterexample — PASS

The sole new option is `-gpgpu_dtc_l1_short_collect_first`, default OFF. In finite `PAPER_OO`, the production LDST ready selector retains the old oldest-ready choice when OFF. When ON, it may inspect at most three additional positions within a four-position PIB window and select an already-ready cacheable load with at most four sectors ahead of an older, not-yet-collecting load with more than four sectors. At eight ready cycles, the older load regains priority. The existing four-sector collect quota, one-cycle collect-to-retire separation, operand writeback grant, Ref ownership, and completion path remain in force. The code excludes non-load sidecars as an ordering boundary and rejects unsupported modes. See `src/gpgpu-sim/dtc-l1-common.h:115`, `src/gpgpu-sim/shader.cc:2748`, `src/gpgpu-sim/shader.cc:3617`, and `src/gpgpu-sim/shader.cc:4438` in the candidate core.

The directed CPU counterexample creates two legal frontend-ready loads in the same cycle: older UID 201 has six sectors over two line references; younger UID 202 has one sector. OFF chooses 201 and ON chooses 202. This is a realizable finite-service scheduling difference, not an Oracle substitution. Hardware area, timing closure, and critical-path causality remain hypotheses; the bounded lookup is a software resource contract, not an RTL result. Historical downstream queue and credit-full evidence remains a counterexample to assuming a scheduling change must improve application time.

## Gate B: local CPU qualification — PASS, CPU scope only

I independently configured and built the candidate with Release assertions enabled in the test targets and ran `ctest --test-dir /root/data/dtc_finite_service_completion_v1_20261109/cpu_review_build --output-on-failure`: **17/17 passed**, zero failed. The suite covers finite service, completion accounting, generation rejection, progressive LDST, K1 Ref and ledger behavior, source invalidation, and M4 atomic/fence lifecycle. The new LDST fixture launches separate OFF and ON processes from the same test binary with the actual option parser. It exercises the production selector, finite collect, operand-bank writeback refusal, later successful retirement, Ref/ledger conservation, eight-cycle age fallback, and invalid-mode rejection. Its final line explicitly marks payload values `UNPROVEN` and zero kernels/model cycles.

The normal aggregated CPU statistics contain the following stable repeated rows:

| CPU process | `enabled` | `choice_decision_different` | `eligible_choice_different` |
| --- | ---: | ---: | ---: |
| OFF | 0 | 0 | 0 |
| ON | 1 | 4 | 1 |

`choice_decision_different` counts selection decisions, including probes or retries. `eligible_choice_different` increments only after a successful real writeback grant and frontend retirement (`shader.cc:3674`); it must not be inferred from the decision count. OFF follows the old selector path with zero new decisions; the added statistics are observational in that path. Existing qualified tests are reused for 32/64/128-byte grouping, partial masks, old generations, return identity, credits, Ref accounting, pressure/drain, and M4 lifecycle. The new six-sector competition fixture calls the frontend completion method to construct ready inputs; it does not independently traverse the entire response/parent/credit source path. Store, instruction, texture and constant traffic do not receive a new per-path candidate fixture; the candidate's cacheable-load selector scope and prior qualification are the basis for their exclusion. Neither CPU result proves application trace exposure, numeric output equivalence, or speedup.

## Gate C static route — PASS_STATIC_ONLY; science admission HOLD

I read the static route at `/root/data/dtc_finite_service_completion_v1_20261109/evidence/gate_c_static/first4_route.py` and independently ran `--check-all` without writing a request. All four allowed witness choices (`ATAX`, `BICG`, `GESUMMV`, `MVT`) returned four cells and 271 effective options. Main's proposed first witness is **GESUMMV**, paired with **vectorAdd** as the structural negative control. GESUMMV is an opportunity selection; no natural ON event or application effect has been observed. Each static pair uses the same 270 historical DH-P0 options plus the one candidate bit, with Oracle mode absent from the new source options and ideal memory/L2 disabled. The route checks the input binding and historical spec hashes and workload shape.

The reviewed route script SHA256 is `d421f2257558f793d4da3043fc4082f37fb30d944beab78f1fee7d6f74b6abab`; the proposed GESUMMV four-cell static manifest SHA256 is `765de6bfd0c1c26b326589914f0ff78088ef9260297c0b30151915833a0ae0c7`. The contract input matrix SHA256 is `09d1257c532269bab41d2cf845399482812ce02e54e02897ae46e72cedec4a4a`; the fixed CORE32 input index SHA256 is `0ae69ed6c73d38415b0f10344a0d2f50e960c6a0324d48c8763a7760d87fdab1`. I re-ran `--check-all` after the script acquired explicit hash pins; it still passed. The build receipt's binary and library hashes matched the actual files, and `ldd` found the isolated `libcudart.so` only when `LD_LIBRARY_PATH` named the isolated core build.

**Gate C1 is HOLD; do not start the first four cells from this static draft.** Before any start, Main must freeze one new Goal-specific request with a never-used UID/UUID and four-cell budget, bind each executable config and its SHA to the frozen binary/library/framework, and prove effective argv/options plus PID/start/maps/loader, working directory and resource guard through the single scientific dispatcher. The Goal-specific strict verification, true164 `SOURCE_KEEP` archive, and typed native restore route must also be established. The old Oracle/native route belongs to another cohort and cannot supply these identities. Only a natural ON event after lawful execution can establish mechanism exposure; if it is absent, stop before the remaining 16 cells.

At this review: **new scientific requests 0; UUIDs 0; model starts 0; accepted cells 0; scientific budget consumed 0**. Gate C2 is not open. This receipt authorizes no science by itself.
