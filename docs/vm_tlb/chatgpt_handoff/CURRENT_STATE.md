# Current state

## Track A status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION` progressed through:

- G2-1 mapper + finite L1/L2 TLB: PASS
- G2-2 translation MSHR / same-key merge / backpressure: PASS
- G2-3 finite PWQ + fixed-latency walkers: PASS
- G2-4 real stall/replay validation: **BLOCKED**

M3 has not started.

## Current blocker

At Core checkpoint `c1431e01f593719f9201d4ad4d7666bebead8a4f`, all M2 directed tests and the standard build pass, but real functional-VM trace replay cannot yet provide acceptance evidence.

Observed diagnostics:

- QV100/RTX3070 functional-mode attempts showed abnormal memory growth;
- a tiny one-kernel trace (`~54 KiB`) still grew to about `65 GiB RSS` in roughly 41 seconds;
- with a 10 GiB virtual-memory limit, the simulator deterministically throws `std::bad_alloc` just after memory-subpartition initialization and before useful trace replay;
- GDB could not start the inferior under that limit.

This is treated as a **runtime allocation diagnosis blocker**, not as proof that a larger-memory host is legitimately required.

The intended M2 VM structures are finite and small. M1 baseline runs previously completed on the same project environment. Therefore the next step is to isolate the first offending commit/allocation and compare mode 0/1/2 on the same head before considering a larger host.

## Current authorization

Execute:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M2_RUNTIME_MEMORY_DIAG.md`

Active goal gate:

`M2-D_RUNTIME_MEMORY_DIAG`

Codex may implement a minimal source/config/integration fix without another human pause only if root cause is directly established and the fix does not change frozen VM semantics or weaken resource modeling/tests.

If M2-D + original G2-4 PASS, resume automatically:

`M2 closeout -> M3 -> M1-M3 macro closeout`.

## Source anchors

Core/GPGPU-Sim:

- baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- G2-1: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`
- G2-2: `740d96f8be80977c150ffc911063969cafd25b8f`
- G2-3: `e579c40d907c201728331a1208c64bb18b869549`
- G2-4 checkpoint: `c1431e01f593719f9201d4ad4d7666bebead8a4f`

Framework/Accel-Sim:

- baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- blocked report commit: `200e6ddf14b6247a25c6aa4108195ee0904702d8`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Frozen modeling decisions

- trace address is simulator `SimVA` by modeling contract;
- translation produces `SimPA`; preserve both identities;
- identity bring-up keeps `SimPPN = SimVPN`;
- translation is on approved coalesced transactions before real L1D/data access;
- M1-M3 study resident-memory translation only: no page fault/migration/UVM oversubscription;
- TLB persists across ordinary kernels in one simulated context unless invalidated/reset;
- PTE requests in M3 will be physical and non-recursive.

## STOP boundary

Do not enter M3 until G2-4 real functional VM replay passes.

Do not classify this as a host-capacity requirement without same-head baseline/mode-control evidence. Stop if diagnosis requires changing frozen VM semantics, if baseline transparency regresses, or if bounded diagnosis cannot be performed safely.
