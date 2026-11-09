# EP-L2 + DTC-L1 — 174-new native research lane consolidation (2026-10-23)

**Status: read-only coordination handoff, not a scientific-start approval.** This file prepares **two new long-lived research windows** and retains **Lane T as on-demand shared storage/runtime maintainer**. It does not start new Codex windows, install science jobs, migrate cold assets, change the epoch-2 authority, write original scientific ledgers, or remove any historical evidence.

## 1. Confirmed native execution authority

- Verified delivery: `swayhrl/accel-sim-framework` commit `4a4931b2ac798c870df5b4661702dfec4900b331`, `docs/ep_l2/operations/174new_direct_native_takeover_20261023_v2/`.
- Entry on 174-new: `source /root/data/ep_l2_dtc_l1_native_v2/activate.sh`.
- Management epoch1 is preserved; **science epoch2 is ACTIVE with 174-new native execution**, original174 official new dispatch administratively retired. **No new science starts are authorized by cutover**. Existing new migration qualification Q1/Q2/DTC Q1/legacy NN are paid and consumed; future native science budget currently **0**.
- Historic Source EP registry unchanged: original174 **57 actual starts, 44 COMPLETE_VALID, T0=1792414193**. Historic DTC AG8R1 route-repair cohort unchanged: **2 consumed of 2, 1 accepted**, and other old cohorts tracked separately. Distinguish these from **four separately charged native-migration starts** (EP Q1 stopped and Q2 accepted, DTC AD-GEMM accepted, separate DTC legacy NN accepted).
- At present `asset ensure` passes only the exact frozen `EP_VECTORADD_S` and `DTC_AD_GEMM` trace collections (plus independently qualified legacy NN provenance); other old174 overlay assets are **NOT automatically local**. They require an exact owner-approved **COPY_ONLY** input selector and true164 archive/materialization. Never claim all old workloads now have qualified I/O throughput.
- New science hot writes are 174-new local ext4, not SSHFS. Immutable complete results use the verified sole-receiver outbox into genuine164 with full SHA and independent native Target restore. Historical originals remain SOURCE_KEEP; this handoff authorizes **0** source unlink/move/rewrite.
- This handoff reads published Git states. It is **not** a new live process check on 174-new. Before acting, query project status and current owner/lease/registration.

## 2. Rationalized lanes (permanent 2 + shared 1)

| New Codex window | Role | Owns | Must not do |
|---|---|---|---|
| **EP-MAIN / 174-new** | EP-L2 science + mechanism + integration + accepted experiment design + paper evidence | A2 producer results, B W/V, C RO/Tag certificate, D attribution, E2 scientific qualification/ledger, F environment history; prepares own native epoch2 spec | No old E2 controller launch, no inherited old budget, no generic old raw refetch |
| **DTC-MAIN / 174-new** | DTC-L1 science + mechanism + AG/BA convergence + evaluation + paper evidence | Original IO/OO and complete L1 design, AG8R1 strict/negative/hold, BA execution constraints, AA/AB/AC/AD/AE/AF/AG mechanisms; prepares own native epoch2 spec | No old AG8R1 retry/refund, no assumption old Git manuscript is newest |
| **T-OPS / 174-new (on demand)** | Common native runtime, immutable asset materialization and true164 storage/recovery | Exact toolchain/input path maps, sole receiver, restoration and resource attribution, legacy archival mapping | Not a new scientific owner, not a second controller, not a permanent background scanner |

Default is **one research window per paper + a shared on-demand Ops window**. Where substantial parallelism is scientifically useful, either MAIN may issue a **temporary, finite execution/review sub-lane** with a signed exact goal and isolated branch/worktree; merge the result into MAIN and close the temporary lane. Do not recreate standing A–F plus DTC 10-lane meshes.

## 3. Historical EP lanes: keep deliverables, retire old interactive windows

As last Git-publication evidence, not a live session census:

| Old lane | Latest verified Framework HEAD | Role/status and disposition |
|---|---|---|
| A2 | `f7869e5dfdc1b6659a1b82a732fcd6ca12f81ddf` | Producer/Core E59 formal observer delivery complete; IDLE. Import exact code/evidence into EP-MAIN as candidate, **not automatically adopted by new native binary** |
| B | `1af7a81629a90db4948f0842a4a9ca2659e6609d` | W/V review complete, IDLE; preserve historical adverse/positive observations |
| C | `ef6d9127eb4882229efc561d832a5985780cea60` | RO/Tag/SGEMM certification and E59 carry-forward delivered, IDLE; certificate is not automatic E scientific acceptance |
| D | `0d8fec555d9ec8582404fe17b6eae06922dc8a95` | Offline attribution/diagnostic and E59 funnel plan delivered, IDLE; numeric intake only after E acceptance |
| E2 | `7c2f830175f40e16651eab4a3cd3a7af73e9927b` | Original174 57 attempts/44 valid, owner-requested pause; controller STOPPED. Freeze registry/T0/failures and accepted pairs unchanged |
| F | `ab8e04dce031aee26e9f92e1b9cebe88fd9f8c2f` | Historical environment/conditional deployment evidence, IDLE/blocked; no new independent F executor needed by default |

A2/B/C/D/E2/F original Git branches, source artifacts, accepted negative results, receipts and raw scientific identities stay archived **as-is**. Do not reset/delete worktrees, rerun old Goals, or copy opaque old Codex session state. The EP native project must track separate scientific lineages: old main61 Core `d010911e3174a3764791183cd108fe4664ba8731` vs newer diagnostic E057 and E59 producer candidates; scientific claims cannot cross-attribute.

## 4. Historical DTC lanes: consolidate by scientific question

- **AG/BA execution and strict acceptance:** currently published old cohort `hrl/iscas2027-dtc-ag8-finite-resume-174-v1` @ `75706e8a0e58309087c4eadb6280f7f3578bcb76`. AG8R1 Source actual 2/2, one AD_GEMM accepted, AD_Gaussian not accepted; preserve full terminal and consumed attempts. The new 174-new DTC native long AD_GEMM and separate NN qualifications are new cohort evidence, **not** retroactive repair of the old failed AD_Gaussian.
- **Mechanism and scientific analysis:** prior AA/AB/AC/AD/AE/AF/AG, X/Y/Z, SG and validation branches are reference libraries of implementation deltas and accepted/negative controls; DTC-MAIN imports only mechanisms relevant to the next scientific question, with exact commit provenance. Do not resurrect all lane instances or automatically merge every branch.
- **Paper:** use the **latest manuscript artifact explicitly approved by the user**, not whichever old Git repo file is easiest. Earlier supplied DTC English v0.23 was a user-confirmed working mother at that time; Git v0.18 is older. Recheck whether a later mother exists. Preserve original IO/OO attribution, original 44-row experiment roles and three historical Hotspot HOLDs, separate modern/independent cohorts, and DC area/timing placeholders.
- Only DTC-MAIN may nominate a new epoch2 experiment after a **new exact scoped budget**. Current AG8R1 0-remaining is not replenished by moving container.

## 5. Shared discipline / next scientific work

1. On 174-new, verify `project status --project EP_L2` and `project status --project DTC_L1`; pin latest published science owner snapshot plus effective epoch2 `run-native` source and native registry.
2. Each MAIN creates an independent science branch/worktree **within approved ext4 space**. Do not edit the frozen qualified binary/source/config/trace for old accepted runs; opt-in any new mechanism. First output is `CURRENT_SCIENTIFIC_STATE.md` (accepted results, negatives/HOLDs, unknowns, pending owner actions) and one prioritized `NEXT_SCIENTIFIC_DECISION.md`. Prepare experimental plan, no execution.
3. When an actual experiment is approved, qualify exact runtime source/config, budget, new request ID, fresh physical pool reservations, and selected input via `asset ensure` or the on-demand T selector. No legacy same-path assumptions, no unbounded promises about NAS read performance.
4. Execute only via current 174-new native epoch2 **sole science入口**. The correct trace path and data source must be resolved to the 174-new local/P1 qualified compatibility mapping or true164. No SSH to run old174 simulator.
5. Original scientific acceptance -> typed immutable result COPY_READY -> true164 archive -> whole-file hashes -> independent native restore -> Source KEEP. Any later new-output reclaim requires a separate exact owner/user approval, not this doc. Keep all historical assets unchanged.
6. Manuscript edits never silently promote drafts or replace mother. EP earlier source authority is EN-v22; ChatGPT EN-v24 was an isolated candidate. Confirm current revision with user if changed. DTC earlier was English v0.23 user package, not remote v0.18.

**Immediate authorization from this handoff: READONLY onboarding, code/asset indexes, research planning and draft edits in isolated worktree ONLY.** No new scientific native starts, no source deletion, no requalification of completed results.

## 6. Suggested startup

Open TWO fresh 174-new Codex windows (one EP-MAIN, one DTC-MAIN), read `EP_MAIN_BOOTSTRAP.md` or `DTC_MAIN_BOOTSTRAP.md` together with this file. Keep Lane T closed after its completed Goal; wake only for a concrete signed asset/storage/runtime task. Results should use the existing GitHub coordination artifacts and the same active ChatGPT scientific review, without introducing new permanent lanes.
