# Text-only source review and limits

The original frozen SEM1_GOAL and all12 rows of LITMUS_MATRIX.tsv were reread, together with the entire1fcf fixture, diagnostic bridge, relevant production LDST paths and frozen Core specification. Review used source/Git metadata only: no C++ compiler, syntax check, AST, fixture import, test, resource sample or process dispatch. All compile/runtime conclusions below are intended assertions, not observed results.

## Actual component route

make_load creates one synthetic pre-coalesced cacheable global access. sm_t::issue passes it through real LDST issue, scoreboard reservation and PIB admission. The real lower-request transport captures actual mem_fetch root UIDs. sm_t::build constructs four explicit sector replies per emitted root; the payload comes only from independent producer state. Expected byte snapshots live in a separate fixture request map and are never passed to Core hooks.

Existing shader.cc at1fcf:3380 binds the actual access physical identity; :3481 accepts the returned root/sector payload into oo_frontend physical-generation storage; :3585 advances the diagnostic cursor only on actual finite collection delta; :3614 records successful WB retirement. Those production and bridge blobs are byte-identical in the new branch. The comparator reads only bridge collection samples. Bind/collect output joins real UID, SM, physical generation, actual PIB slot/generation, sector, collection and retirement component time. It does not read reference memory as a load result.

The new target uses -fno-access-control solely for component driving and inspecting real state. Positive scenarios do not assign frontend lifetime/notification/generation fields. Only explicitly named negative controls mutate an actual inflight generation or waiter, or call the real release assertion illegally. Geometry stays64sets x8ways,640physical lines,128PIB,4allocations/cycle and4Tag banks at1request/bank/cycle. AE/AD/K1 are diagnostic knobs only; global provisional K0 is unchanged.

## S02: logical eviction while physical Ref is live

Nine distinct128B lines separated by64x128 bytes contend for one64-set logical set under AE0. All replies are withheld untiltick90. The source requires the first A allocation to remain allocated, lose Tag visibility, retain Ref>0 and have no collection while all nine bindings exist. The eventual old consumer compares accepted A bytes against A[i]=i after normal WB. B has255-i; the swap negative changes only A/B packet bytes, requiring actual comparator mismatches and exit1. The old consumer's physical identity is never replaced by a current lookup. These assertions are unexecuted.

## S08: late merge, early retirement and genuine PIB slot reuse

With AD enabled,32 initial consumers of A arrive before its return. Four notifications/cycle give an eight-tick broadcast interval, sufficient in source analysis for collect+1, successful WB, and a later issue to reuse the freed first slot. This larger S08 fanout is separate from S12's original at-most10consumer bound and stays below frozenPIB128. No notification quota, retirement latency or buffer capacity is changed.

Arrival is state-driven: issue a late A while the actual physical line is data_ready but not broadcast-ready, then issue B only after the first actual bridge retirement and while notification remains incomplete. The source requires the late A's same physical generation plus actual late_merges>0, and B's same PIB slot with strictly newer slot generation. B contains0x55. Successful normal completion requires exactly34 consumers and two lower roots. Finite tick250 is a failure bound, not a silently extended retry. Whether the real scheduling window satisfies every assertion remains UNPROVEN until separately released execution.

The stale-waiter negative redirects an actual still-unnotified A waiter to the reused B slot/generation. The next production advance_service should reject owner && has_reference(owner,A); a generic abort or unrelated assertion is not enough. No negative-control result currently exists.

## S11: two real SM-local caches; no new coherence

Two actual shader cores each have their own LDST, physical pool, diagnostic bridge and real return path. After both old A loads retire, the fixture externally publishes byte0=0x99 and directly invokes selected IDLE_CLUSTER E only on SM0. SM0's new load must issue a new root and collect153. SM1 must retain its old physical identity, issue no new root and collect0. Its comparator uses a retained-route expectation; the stronger freshness predicate remains UNRESOLVED. The program does not execute a store, model inter-SM publication, qualify source E's upstream guard, or demonstrate architectural cache coherence.

## S12: bounded combinations, not an exhaustive proof

One invocation takes a fixed index0..63. Xorshift32 starts at0x53454d31, with fixed unsigned arithmetic independent of time, UID and host scheduling. Schedules vary AE/AD, sector permutation, masks0..3/31..32/64..71 and explicit external publication with or without selected E. Each issues eight earlier and two later consumers over A/B and applies four real RF-bank conflicts. Old references can remain alive across E. No source mem_fetch/physical bytes are inferred from reference state.

Index0..57 intend conditional positive routing;58 intends the conditional no-E stale-byte countermodel;59 bad-byte,60 missing-sector,61 wrong-generation,62 early-release,63 false-publication are targeted negatives within the same64-index bound. False publication is rejection of the explicit freshness contract without E, not a claim that K0 violated an implemented coherence protocol. The latter five do not count as positive value tests. No schedules have been executed.

The counter increments for each LDST tick, issue, offered fill, external publication, E and real RF interference; max96+10+16+2+4=128. Reply construction is preparation for a later counted offer, not accepted return evidence. Internal automatic allocations/notifications/collection/WB mutations are not separately counted. Thus a complete internal event census and exhaustive128-event combinations are UNPROVEN, and the12-row matrix labels S12 PARTIAL_SOURCE_PREPARED. The fixed96-tick drain deadline is intentionally tight to preserve the bound; if execution cannot drain or induce WB blocking, that is an engineering failure requiring publication and review, never evidence of a value pass or permission to extend the contract.

## Remaining scientific/engineering gaps

S03 still lacks an old root arriving after true physical-slot reuse; corrupting a live generation is narrower. S06 lacks partial31/32 publication plus source-backed C/D distinctions and old-consumer route over that exact publication. S09 lacks a deliberately forced unnotified fifth collection attempt. S10 lacks a controlled AE-off/on two-line identity differential. New masks do not establish functional lane gather or upstream coalescing. Arbitrary alias/race programs, architectural registers, stores/atomics/fences and coherence require additional semantics and are outside this diagnostic.

No actual artifact, static ELF identity, compiler flag manifest, source-bound new classifier or finite runtime registration exists for this new target. Proposed commands reuse the known toolchain form, not the old output/cache/ELF. A fresh parent-admitted matching-ABI build and static freeze are required first. Expected SIGABRT requires the exact injected marker plus correct source assertion; unrelated abort, resource STOP, timeout, cleanup failure, missing library line or exit71 is failure. New runtime code must preserve own retained-Popen/pidfd cleanup and strict >5GiB disk / host+cgroup resource conditions. The existing ten-mode CPU role has no authority over these new argv.

Source preparation does not alter original contracts, claim acceptance, AG4/AG5/AG6 budgets, production policy or parent live code. Incidental Git commit output advertised its automatic housekeeping; subsequent publication commands explicitly disabled Git automatic maintenance per invocation. No test or build process was launched.
