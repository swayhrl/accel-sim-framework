# P2 engineering candidate: two distinct line-slot operations/bank/CORE tick

Status: **CPU_FUNCTION_AND_NI_PASS_PENDING_MAIN_SOURCEQ**. Independent branch
finite/full-f-payload-bankops2, Core92ed2c4c1c2d682b33f2f7ce4d6b56571a889480
(parent78f4b59e?), tree967ee1804ec9e4346aad4059439fcb1576d854ed.
No scientific model, native entry, registration, budget, accepted point or merge.
The built accel-sim.out was never executed, including help. Main alone may review
and adopt this exact identity, requalify host/Source/native-loader evidence,
create matched new-Source S/F references and start finite scientific cases.

## What is implemented

Four banks, <=2 **different physical line-slot** operations/bank/physical CORE
tick. Any second operation on the same physical slot, including R/R, RAW, WAR,
WAW or new generation after reuse, waits for a later tick. This conservative
policy avoids undefined SRAM read-during-write/dual-write behavior. It is not
arbitrary same-address2RW RAM, two new frontend/fill/response ports, or2x end-to-
end bandwidth. A logical grant may be a sector response/fill or line WB/copy;
do not assign a uniform byte width. Physical payload remains1168 modeled128B
line slots/slice(9.125MiB/64 slices), four banks, all existing queues/D512/
LineMSHR128/WAD128/copy latch and all input/frequency settings unchanged.

Production changes are four files, plus two test-fixture capacity predicates
generalized from <=1 to <=actual bank_service_limit (asserts are retained):

| New Core file/function | Lines | Binding |
|---|---:|---|
| gpu-cache.h::bank_identity_enabled |2343|P2 S and F retain exact role/localID/write/client/token/generation; P1 boolean unchanged|
| gpu-cache.h::release |2583?2589|P2 release cancels old pending/selected identities; never refunds service|
| gpu-cache.h::request |2703?2776|Retained selected identity remains until actual retry; same-slot selected predecessor blocks younger retry; no duplicate queue entry/logical count|
| gpu-cache.h::request immediate grant |2737?2746|Only remaining paid services and an unserved physical ID may grant|
| gpu-cache.h::consume_bank/p2_slot_served/p2_selected_predecessor |2851?2873|Direct two-ID scoreboard/bank; selected-age ordering; no address probe or directory/CAM lookup|
| gpu-cache.h::p2_deny |2932?2939|Conflict/retry/wait counters retain their original populations|
| ep-l2-rg1.inc::cancel_transaction |99?104|P2 native cancellation works without enabling RG1|
| ep-l2-ro-store-port.h::constructor/fill_write/response_read_identity |21?26,68?98|Finite1168 banked FT2 accepts P1/P2; actual packets still pay real fill/read grants before mutation|
| gpu-cache.h::validate_ep_l2_mode_config |3382?3463|Open P2 only in reviewed finite contexts, preserve S64/quota/MQ2/RG1/ideal/fixedTVD/local-free diagnostics exclusions; new >1024-Tag P2 guard|
| ep-l2-ft-cache.inc::ft_print |676?693|P2 is not labelled P1-eligible; explicit P2_POLICY reports same-slot serialization, retained identities and denials|

Actual RO runtime constructs store_port with native_request_ids=true at
ep-l2-ro-runtime.inc34. P2 qualification covers this real production adapter,
not legacy GENERIC/token0 facades with native_request_ids=false. Those facades
are not certified as multi-packet P2 identities. No new T/reuse_seen eligibility,
Tag probe/replacement query, response queue operation, allocation/free policy,
sector/pin/generation/WAD protection or scheduler action was added. RO detach,
late-fill Tag-generation checks and retirement code are unchanged. The actual
S copy phases remain independently paid and separated by their original cycle
boundary(ep-l2-ft-cache.inc466?490). Preview still commits no arbiter population.
The P2 index comparisons inspect at most2 serviced/selected IDs in the existing
bank; maximum4 native pending heads is still asserted.

P1 executes its original matching, budgets and semantic branches. New physical-ID
array32B plus statistics counter8B increase C++ store sizeof1160?1200, independently
compiled against old/new headers. At64 stores that is2560 host bytes, common to
new-Source S/F/P1/P2. This is not a synthesized SRAM/area estimate. A conceptual
1168-slot physical ID needs11 bits; the added2 IDs/bank and comparators have real
hardware/clock costs that remain UNKNOWN. Source-only reading does not prove
<=5% host overhead. No throughput, performance speedup, PPA or full-application
correctness claim is made.

## What actually ran

* Actual header-only old/new controls(3f578179?): compile old78 and candidate
  independently; original P1 semantic lines match byte for byte in S and FT2.
  Old generic P2 grants all four same-slot combinations within one tick; the
  new defined conservative policy refuses the second until a later tick.
  New S/FT2 retained reverse-order retries, multi-cycle absence, native-head
  identity, cancellation, generation reuse without refund, preview32,
  independent same-bank2 service, no third grant and pending0 all pass.
  This old capture is a policy-boundary counterexample, not an allegation
  that previously unqualified full F P2 produced an accepted wrong result.
* Full private Core+Framework/static archive+ELF+4 CPU targets build PASS,
 247.46s, one CPU/nice10, AS2GiB/process, monitored process-tree RSS<=2GiB,
  private total237,244,416B at completion and total envelope1GiB. All new cache
  CPU objects use the new headers and all new Core archives. No new-header/
  old-library link is used. Framework9dd/vendorf90 are independent copies.
* Actual production CPU50 executions/20 same-binary OFF/ON comparisons
  (15e6713a?):10 old78 P1 references +40 new P1/P2 runs. For each of10 controls,
  new P1 semantic fields/digest/cycles equal old78 byte for byte; each P1 and
  P2 Observer pair also matches byte for byte. Actual versions/exact-once,
  ownership, generation, pins, quota and full drain assertions are retained.
  Cases: sector overlap/reentry, RO merge population, real TagFAIL/preview32,
  detached old return after Tag reuse, TVD zero duration, real WAD early reject,
  pressure-eligible detach, Tag-pressure joint capture, response backpressure,
  native requester versus RO victim.
  All ON runs have actual LIFE terminal wire and fixture asserts closed/invalid0.
  The Tag-pressure joint fixture requires R4/R5 ON in both arms; only LIFE/ET
  requested flags vary there. Other nine controls compare all four heavy flags
  OFF/ON. ET has no final/global-clock wire in these component runs: **global
  ET timeline noninterference/closure is not established by this matrix**.
* Additional24 engineering executions(592fd2ca?): actual static-S production
  cache copy/fill/response/frontend/WB interleave at P1/P2, each OFF/ON and
  complete drain, actual bank peak2 achieved in P2;1 external-harness compile;
  four geometries(32/64 sets?8/16 ways)?S/F?P1/P2=16 actual production
  constructor/getter cases; P3/S64+P2/RG1+P2 reject through original guards.
  F cases run the current Source's real RO loader and whole-commandlist
  binding with actual Conv certificate, including both32?8 and other geometries.
  Source/certificate/command refs and all six new archive hashes are retained.
  No GPU object, cycle or Trace body is created/read in constructor/loader cases.
  The S interleave fixture drives direct cache CORE ticks, not detailed DRAM/
  SM clocks, and lacks LIFE terminal wire: S LIFE closure is NOT established
  by that fixture. Do not borrow the F scope as all-mode/all-clock proof.
* Additional old78-only external S/P1 cache regression(e4bbbad9?): old headers
  with old archives versus the candidate's separately linked test gives exact
  S/P1 semantic equality. This is explicitly a reference, never a mixed link.

All CPU work took fresh read-only engineering admission using the exact current
peer commitments/own growth/floors. The new C07d0a? wrapper skips optional PSS,
retains actual RSS and original admission formulas, and holds a shared metadata
lock only for its bounded snapshot, never compiler/CPU bodies. Actual stages
preserve PID/RSS/limits/command/stdout/stderr/hash receipts. No extra arbitrary
SSD or RAM floor was invented. Builds and tests use a CPU and its SMT sibling
outside active model affinities; CUDA_VISIBLE_DEVICES is empty.

## Preserved engineering holds/failures

The first Framework local clone failed on an unrelated absent Git objectf584?
before build; existing clean workingtree and Git metadata were copied with
ordinary independent files, exact Framework/vendor HEAD and clean tracked
status rechecked. No protected lazy fetch or old-source edit was performed.
Early resource samples held on registry/claim transitions, not physical RAM
shortage. The partial CPU run is preserved; only unexecuted controls continued.
A test-runner incorrectly turned R5 OFF for a fixture requiring assert(r5):
that P1 OFF failure is retained, no production/assert change was made; the
explicit required-R4/R5 test scope is used in the passing matrix. A private
old-main wrapper initially lost C++ main's implicit return0 when renaming it;
its complete PASS output/warning is retained, and only an explicit return0 in
the external test copy corrected the indeterminate exit status. Neither is
discarded as a protocol PASS.

## Main adoption/claim boundary

Source5 is new: Core92ed?, Framework9dd?, vendorf90?, mainELF67315b87?,
libgpgpusim.a b1b501fc? . The original Source78 HEAD, ELF78d4? and archivee5a7?
remain unchanged. Do not combine queued/current Source78 accepted S/F points
with new92ed points. Existing source-qualification/application authority is
not inherited. No extra CLI option is registered;282 is expected from unchanged
registration, but actual new native help and full282 output qualification have
not been performed by B.

New SourceQ/producer, exact source/ELF archive provenance, native prelaunch
qualification and small actual matched new-Source S/F references are Main tasks.
P2 requires a new strict host mathematics binding: validate actual bank_ops2
and P2_POLICY, physical1168, bank peak<=2, same-slot policy, and change the
specific hardware_P1_throughput_eligible expectation to0 for P2 with an explicit
P2 eligible declaration. Original P1 expectations must remain1. Current G/P64
math proofs are Source78-bound and must not silently accept the new Source5.
The new constructor/mapping evidence may support a new exact adapter; do not
delete a math guard or pretend old G/RO application acceptance transfers.

Use a finite new-Source P1/P2?S/F comparison at unchanged input, geometry,
queues, clocks and observer profile. Roles remain static S versus unified F at
the same physical1168/P2 service capability. P2 changes actual modeled service
and adds metadata/comparators; it is not a free algorithmic gain. Performance
opportunity and host overhead remain UNKNOWN until measured with the new exact
Source. Candidate is ready for Main review, not scientific launch permission.

## Supplemental normal mechanism-observer NI

Three additional actual P2 production controls compare MS0 against the exact
MS1/heavy-four-OFF endpoints already recorded: detached-old-return generation,
WAD early refusal, and response backpressure. New private overlays alter only
ms_observer1?0; all semantic lines/digest/cycles match byte for byte. Source,
headers and all new archives remain unchanged. Receiptc4308041? reports3PASS,
no model/registry operation. This complements the four-heavy-observer matrix;
it is not a host-overhead measurement or new MS0 application reference.

Policy JSONV2 distinguishes increased bank service capacity from unchanged
caller frontend/fill/response/lower ports. Bank service hardware cost is not
zero; generic ?no ports added? is deliberately not used as a cost statement.
