# Current state

## Track A — repaired M2 accepted

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — independently accepted after M2-RF**.

Accepted repaired M2 evidence:

- Core current repaired head: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`;
- Framework simulator dependency/source repair: `4012be3606c300d11e7b34826ee1cb22b0852b93`;
- Framework M2-RF evidence/report head before this handoff: `c12ad7bc9fb6865e97ff8b65c215490a5d92305a`.

Important history note: Core `3b93e243` is built on top of the preserved provisional G3-1 commit `8c613a356e6a146951cd59c9929046c6c4cfd856`. M2 is accepted by execution-path semantics and regression evidence at that head; this does **not** automatically accept all provisional G3-1 PTE-address behavior.

### Accepted M2-RF result

The reopened pending-waiter problem is closed:

- once `(translation key, waiter UID)` has been accepted into an active translation MSHR, retries of that same waiter return pending before L1/L2 port consumption or TLB probing;
- a new waiter UID for the same key still performs the normal first L1/L2 lookup and may merge;
- exact directed evidence proves one initial A L1/L2 miss, nine A no-probe/no-port retries, B's use of the sole shared L2 port while A is pending, and exact registration/wakeup/completion behavior;
- L1/L2 access/miss counters now represent actual probes rather than same-waiter polling;
- pending-waiter bypass, MSHR occupancy high-watermark, waiter-depth aggregate/max, MSHR lifetime aggregate/max, page-size, PWQ/walker observability are present;
- kernel-boundary persistence has focused test + simulator lifetime source proof;
- cold M1/G2 regressions, disabled/ideal transparency, one-kernel/LUD/BFS functional replays all pass and quiesce;
- BFS walk-latency 5→50 retains seven walks while L2 probes remain 156 and misses change only 16→19; pending bypasses expose the increased wait (57→901), removing the prior polling-driven miss explosion.

The prior 32–65 GiB blocker also remains closed as a stale cross-repository C++ layout/build-dependency issue, not a legitimate VM footprint.

## M3 status — G3-1 still not accepted

G3-0 entry/freeze is historical PASS.

Provisional G3-1 Core commit:

`8c613a356e6a146951cd59c9929046c6c4cfd856` — replaceable PTE backend/request contract.

Independent review found a concrete correctness bug in its PTE-address namespace. Current encoding shifts `(page-size-class, level)` by `vpn_bits(page_size)`, which is 33 bits for 64KB but 28 bits for 2MB. Because the shift width changes by page-size class, namespaces can overlap.

Concrete current-code collision:

```text
64KB, class 0, level 0, vpn=(4 << 28) | X
2MB,  class 1, level 0, vpn=X
```

Both map to the same slot under the current formula. Therefore G3-1's claimed unique `(page-size-class, level, VPN) -> PTE physical address` mapping is not yet valid.

This bug does not invalidate accepted M2 behavior because the M2 execution path uses the backend only to resolve the frozen identity-like PPN and emits no PTE memory traffic.

## Current authorization

Execute only:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_1_ADDRESS_NAMESPACE_FIX.md`

Active gate:

`M3-G3.1-RF — PTE address namespace injectivity fix`

Required high-level repair:

- use one fixed namespace width based on the maximum supported VPN width (currently 33 bits from 49-bit VA and 64KB minimum page) or an equivalent globally injective encoding;
- prove no overlap across every supported page-size-class/level namespace;
- add an explicit directed test for the former collision;
- retain physical/non-recursive request semantics and reserved-range separation;
- rerun repaired M2 regressions and a bounded functional M2 replay;
- correct stale M3 review-pack wording/status;
- do not apply/commit the reported G3-2 stash.

After G3-1-RF, STOP for ChatGPT review before G3-2.

## Frozen / accepted source anchors

Core/GPGPU-Sim:

- baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- G2-1: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`
- G2-2: `740d96f8be80977c150ffc911063969cafd25b8f`
- G2-3: `e579c40d907c201728331a1208c64bb18b869549`
- pre-review M2 closeout: `e7999554200760b31b4efe16d98e050370e1ea71`
- provisional G3-1 parent: `8c613a356e6a146951cd59c9929046c6c4cfd856`
- accepted repaired M2 execution head: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`

Framework/Accel-Sim:

- baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- M2 dependency fix: `4012be3606c300d11e7b34826ee1cb22b0852b93`
- M2-RF review evidence: `c12ad7bc9fb6865e97ff8b65c215490a5d92305a`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Frozen modeling decisions

- trace address is simulator `SimVA`; translation produces `SimPA`; preserve both;
- data mapping remains resident and identity-like for baseline bring-up (`SimPPN=SimVPN`);
- translation operates on coalesced transactions before real data-cache access;
- M1-M3 excludes page fault/migration/UVM oversubscription/MCM;
- TLB state persists across ordinary kernels in the simulated context;
- M2 TLB hit latency remains a functional zero-latency `MODELING_DECISION` with finite ports; timing-realistic lookup latency belongs to M3;
- M3 PTE requests are physical and non-recursive;
- generic PTE/radix details are `MODELING_DECISION`, not Segmentation-paper exactness.

## STOP boundary

Do not begin G3-2 real PTE L2/DRAM integration until G3-1 PTE-address injectivity is fixed, directed-tested, pushed, and independently reviewed.

Stop on any M2 regression, PTE namespace alias, reserved-range overlap, recursive translation, source/provenance ambiguity, or any need to apply the unreviewed G3-2 stash.
