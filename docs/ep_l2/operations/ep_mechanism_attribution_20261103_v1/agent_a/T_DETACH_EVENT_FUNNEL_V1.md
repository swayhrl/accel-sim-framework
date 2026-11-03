# T detach actual-event funnel V1

Status: **PASS bounded offline counter and Source audit; PARTIAL causal attribution**. No new model, CPU fixture, Trace scan or raw streaming pass was performed. This report uses accepted small JSON, the three same-mode NI receipts and read-only production source. The reproduction script is `derive_t_funnel.py`; exact input SHA, population definitions and source anchors are in `T_COUNTER_POPULATION_AUDIT.json` and `OFFLINE_EXECUTION_RECEIPT.json`.

## Scientific scope and result

All three Conv16x8 arms use Core `1e07b263ca0879798387d2a712914a914f298775`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`, vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`, ELF `54c3fbba9bb152d1a26539cccb617ac4a3368547a06509f427a202eeda6d8505`, library `4ea74720bec776712d56b84e493c376d364691d6eae40267f52bc836c703e2db`, input `438eefd67b073f1ca0e2c08be6aa99b3b9b9619d7832cc6cad9cc4467e63654e`. Geometry is 64 slices x 16 sets x 8 ways, 32 DRAM channels, dram_latency=100. All six OFF/ON points are accepted and drained: 714,547,200 instructions, 27,648 CTA, two kernels. No result from Source78 or a different geometry is spliced into this T contrast.

**PROVEN:** T has real joint full-set/releasable-RO opportunities in this input. Legacy-F reaches 237 detaches; Corrected-F reaches 360, and the old detached transactions all retire. The corrected ordinary-request path is operational and pays its declared shared metadata-query cost. **PROVEN:** Corrected-F is still slower than F-minus-T in this complete matched input. More detach is therefore not a demonstrated net optimization here.

| Final cumulative metric | A F-minus-T | B Legacy-F | C Corrected-F |
|---|---:|---:|---:|
| GPU cycles | 362791 | 367152 | 364463 |
| Covered frontend head-cycle observations | 7488836 | 7497825 | 7498487 |
| Passive raw Tag FAIL, jointly R=8 | 311545 | 322938 | 320603 |
| Same snapshot contains a live RO | 136627 | 148539 | 146882 |
| Same snapshot contains structural eligible RO | 27333 | 13012 | 724 |
| Operational eligibility count | NOT_APPLICABLE T=0 | 13012 | 724 |
| Raw-full frontend allow decision | 809 | 875 | 1767 |
| Virtual-MISS preview after consultation | 0 | 237 | 360 |
| Actual backend raw TagFAIL / relieve / detach | 0 / 0 / 0 | 237 / 237 / 237 | 360 / 360 / 360 |
| Triggering access accepted in this ft_access | 0 | 237 | 353 |
| Triggering access denied in this ft_access | 0 | 0 | 7 |
| Old detached fill packets / responses / retirees | 0 / 0 / 0 | 237 / 237 / 237 | 360 / 360 / 360 |
| Ordinary paid queries / slice GPU wait exposures | 0 / 0 | 0 / 0 | 2954 / 2954 |
| Ordinary shared-port wait attempts | 0 | 0 | 0 |
| Same-mode compact OFF/ON NI | PASS | PASS | PASS |

B vs A adds 1.2021% cycles; C vs B removes 0.7324%; C vs A adds 0.4609%. The 2954 query wait exposures are sums across slices and cannot be subtracted from 364463 GPU cycles, or assigned as the cause of the 1672-cycle C/A loss. The 123 extra detaches are not 123 known independent saved misses.

## The funnel has distinct populations

1. **Raw probe / all reserved.** `tag_array::probe` in gpu-cache.cc:365-453 returns `RESERVATION_FAIL` after failing address/sector hit checks when every way is reserved. Dirty replacement preference has a fallback and is not an independent raw-fail reason. The passive pre-preview probe is gpu-cache.cc:3063-3069. TP jointly captures all eight physical way classes, the target set, request UID and physical-cycle context, rather than multiplying marginal counts. The accepted TP raw-fail rows all have R=8 and all eight way exposures are RESERVED.
2. **Old RO live / structural eligibility.** gpu-cache.cc:3093-3098 snapshots each target-set way: live, attached, reuse_seen, required and ready. Eligible means live && attached && !reuse_seen && (required & ~ready). `can_detach` and the real detach use that same predicate, ep-l2-ro-transactions.h:211-230. `reuse_seen` is set by an accepted merge and persists, lines200-201; it is not reset when a merged waiter leaves. These are current policy facts, not evidence that relaxing the policy is safe or beneficial.
3. **Paid query and pure virtual relief.** The RO path consumes its timed ticket before its production preview probe (ep-l2-ro-runtime.inc:279-303). The corrected ordinary path reads the raw Tag set first and waits for the shared query ticket before consulting eligibility (gpu-cache.cc:2816-2839). The real frontend issues the ordinary ticket only after pure preview, l2cache.cc:1356-1364; the shared port is one issue per slice per physical GPU cycle and ready=now+1, ep-l2-ro-runtime.inc:108-138. Preview mutates no Tag. A successful consultation converts the plan to virtual MISS; it does not itself detach.
4. **Frontend decision versus real backend.** l2cache.cc:1434-1477 gates the plan against MSHR, MissQ, data and response availability. `pressure_prod_probe_reached` means the *production preview* probe was reached, not that `ft_access` ran. Only admitted attempts enter real access (1591), whose raw Tag probe, paid-ticket guard and actual relieve are ep-l2-ft-cache.inc:327-343. Thus A has 311545 real full-set frontend exposures but zero backend TagFAIL: blocked requests do not reach this backend counter. Reporting backend zero as no Tag pressure would be false.
5. **Detach versus immediate acceptance.** The backend can still deny after successful Tag release: directory, capacity, held transaction, WAD, pin, MSHR, MissQ, landing and bank/service gates remain. `commit_scope` records whether that *same ft_access invocation* accepted after a detach (ep-l2-detach-diag.h:304). For C this is 353 accepted and 7 denied. These are not 7 lost application requests. Their specific resource cause and later UID-linked accept/complete times are not instrumented in the compact projection. Global bank-denial counts must not be used to fill that missing joint.
6. **Old RO return / retirement.** The detach handshake invalidates the old Tag, unbinds Payload and increments Tag generation (ep-l2-ro-runtime.inc:179-203). Detached fill writes the old Payload identity and does not call Tag-ready (ep-l2-ro-transactions.h:256-273). Accepted responses release their descriptors (300-313); retirement waits for no waiters/prepared response/missing or in-flight sectors, then unpins/releases detached Payload (396-404). Actual counters close: detaches=old detached retirees=237/360, live_detached=0, and total RO admits=retirees, admits+merges=responses. This is event-count conservation plus accepted invariant checks, not a new numerical-output proof.

## Eligibility 13012 versus 724 is not an opportunity-loss comparison

Both values have the same **stage definition**: pre-preview physical snapshot, then once-recorded frontend callback at gpu-cache.cc:3104,3145-3156. `ledger::once(cycle,uid)` (ep-l2-detach-diag.h:250) suppresses duplicate callbacks for the same slice/UID/stamp; it does not make a blocked UID unique across later ticks. Their denominators are B=322938 and C=320603 raw-full head-cycle observations in different simulated trajectories. They cannot be divided against one another as the probability a common population loses a detach opportunity.

The actual TP joint tuples retain requester class, eligibility, route, frontend allow and early cause for the same snapshot/request/set/time. Reducing those tuples, rather than multiplying marginals, gives:

| Eligible raw-full head-cycle route | A, structural only T=0 | B | C |
|---|---:|---:|---:|
| Certified RO candidate, paid-query early reject | 194 | 239 | 301 |
| Certified RO candidate, consulted FAIL | 18296 | 0 | 0 |
| Certified RO candidate, virtual MISS and allow | 0 | 237 | 297 |
| Ordinary native path, relief not consulted, deny | 8840 | 12536 | 0 |
| Ordinary native path, paid-query waiting, deny | 0 | 0 | 63 |
| Ordinary native path, virtual MISS and allow | 0 | 0 | 63 |
| Ordinary native/TVD early fallback, allow | 3 | 0 | 0 |
| Total | 27333 | 13012 | 724 |

**PROVEN:** B exposes 12536 ordinary/full/eligible head-cycles that never consult relief; C exposes 63 ordinary eligible query-wait and 63 ordinary eligible virtual-MISS/allow head-cycles. This verifies the intended changed production route. **LIKELY:** changed release and request timing contributes to the much smaller C eligibility exposure. **UNKNOWN:** how much of the difference is repeated waiting, distinct UID changes, later eligibility transitions or other scheduling effects. Saying the repair 'eliminated 12288 waits' would exceed the evidence.

The non-RO class includes ordinary reads, writes and native writeback paths; it is not strict independent demand NEW. The compact joint no longer retains individual UID/set/time values after reduction; its producers enforce them at capture time. No cross-arm UID join is available.

A's operational detach diagnostics intentionally do not census eligibility when T=0; their zero must not replace the independent TP physical snapshot, which measures 27333 structurally eligible full-set observations. In B/C, eligible0 histograms plus eligible1..8 exactly sum to their own raw-full populations.

For C, no-live-RO raw-full observations=173721, live-but-no-eligible=146158, eligible=724; all 320603 are jointly measured. The latter two categories reflect this conservative policy and trajectory, not an application-wide future-reuse oracle. Ready-only/no-missing exclusions did not appear at these raw-full snapshot bins; reuse_seen does appear. The existing result does not authorize weakening reuse or ownership checks.

## Frontend allow is not detach or final success

A/B/C raw-full allow counts 809/875/1767 include 809/638/1407 ordinary TVD-candidate early=5 fallback decisions for which the production preview raw probe was not reached. Those values cannot be called requests rescued by T. The remaining B/C 237/360 are virtual-MISS/allow observations. Even that allowed plan precedes real access and downstream resource arbitration. C's 360 actual detaches with 353 immediate accepts shows the distinction directly.

Query tickets, head-cycle waits, access attempts, actual detach events, lower fill packets, response waiters and retirees use different units. Their equality in a particular arm must be checked, not assumed from names. The CSV uses separate columns and never subtracts different units. Physical-cycle stamps are `gpu_sim_cycle + gpu_tot_sim_cycle`; callbacks occur on the L2 scheduling path, query latency is modeled in physical GPU cycles. LIFE L2 ticks and DRAM-domain counters are not joined here or relabeled as GPU cycles.

## Remaining measurement and scientific decision

**NOT_INSTRUMENTED / NOT_MEASURED:** strict demand-unique NEW at ingress, distinct first-head UID denominators, per-trigger future acceptance/completion, the resource reason jointly attached to C's seven post-detach denials, ordered request trace NI, numerical application output and physical PPA closure. The first64 diagnostic samples are bounded examples, not a complete chain; their truncation does not invalidate closed cumulative counters.

**Next decision:** retain the accepted three-arm result and prioritize the already authorized W/V decomposition. T should be described as a functional pressure-relief mechanism whose corrected path helps relative to Legacy-F but has no net Conv16x8 benefit over F-minus-T. No extra latency scan, Tag shrink or protection relaxation is justified by this funnel alone.

If a later T engineering change needs per-trigger attribution, the minimum candidate is a default-OFF bounded record at existing paid-query issue/ready, actual detach, `commit_scope::finish` (include denial gate), and existing requester-accept/response-complete notifications. Store trigger UID, selected old Payload/generation, set, physical-cycle stamp and explicit clock domain; track a bounded trigger UID whitelist until completion. Keep ingress and first-head records distinct, with real same-population denominators. Do not add probes or modeled directory operations. This is an unimplemented design only. A new Source/ELF and separate same-mode OFF/ON NI for each actually used T arm would be required before scientific use; current compact NI does not certify the unbuilt collector.

## What was actually done

Executed a bounded Python reducer over 33 distinct small accepted JSON/source inputs (about9.12MB distinct input bytes), verified SHA pins for validation/acceptance/archive refs, exact Source5/input/complete-population equality, TP R8 raw-fail joint, frontend/eligibility/commit/old-RO count partitions, all three compact NI receipts and final closed flags. Full counter copies and exact producer function/line/file-SHA anchors are retained in the JSON audit. No raw or Trace was read, no production file or controller/registry was changed, no CPU fixture or application was launched and no Git write was performed by Agent A. Large accepted assets remain on true164 under their existing archive receipts.
