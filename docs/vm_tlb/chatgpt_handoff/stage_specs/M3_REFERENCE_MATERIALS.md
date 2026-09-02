# M3 Reference Materials and Evidence Boundaries

## Purpose

This file defines what Codex should read before implementing M3, which facts are authoritative for the generic single-GPU VM baseline, and which paper-specific details remain intentionally unresolved until M4B.

M3 must not stall waiting for unavailable target-paper details when a generic, explicitly labeled `MODELING_DECISION` can produce a correct reusable timing substrate. Conversely, it must not present a generic choice as `PAPER_EXACT`.

## 1. Required project materials

Read these first:

1. repository-root `AGENTS.md`;
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`;
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`;
4. `docs/vm_tlb/chatgpt_handoff/stage_specs/M2_M3_TARGET_MODE.md`;
5. `docs/vm_tlb/chatgpt_handoff/stage_specs/M2_FUNCTIONAL_TRANSLATION.md`;
6. `docs/vm_tlb/chatgpt_handoff/stage_specs/M3_TIMING_REALISTIC_BASELINE.md`;
7. M1 review pack;
8. the completed M2 review pack before entering M3;
9. long-lived VM specs under `docs/vm_tlb/specs/` created/updated during M1/M2.

The completed M2 SHAs and invariant results are the immediate M3 source of truth. Do not reason from an earlier pre-M2 code snapshot.

## 2. Target Segmentation paper facts relevant to M3/M4B

Source:
`docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`

Known `PAPER_SPEC` relevant to later reproduction:

- baseline page size: 64KB;
- L1 TLB: 32 entries, fully associative;
- L2 TLB: 768 entries, 16-way;
- page-table walkers: 16;
- the authors implement L2-TLB sub-entry support in Accel-Sim;
- the paper states that it leverages the detailed TLB modeling component of its reference [4].

Important `UNKNOWN`s that M3 must **not** silently invent as target-paper exactness:

- exact L1/L2 TLB lookup latency and throughput/ports;
- exact page-table organization used in the paper implementation;
- exact PWC organization/capacity, if any;
- exact walker microarchitecture/timing beyond walker count;
- exact sub-entry format/fill/replacement/timing;
- exact synthetic-KV interaction with PTW/PTE traffic.

Consequence:

- M3 may build a replaceable generic timing backend;
- M4B may later override target-specific TLB/PTW/sub-entry details when evidence or an approved approximation exists;
- M3 must not implement the target paper's sub-entry mechanism.

## 3. CLAP as a generic GPU-VM reference, not target-paper truth

The user-provided CLAP paper (`Leveraging Chiplet-Locality for Efficient Memory Mapping in Multi-Chip Module GPUs`, MICRO 2025) provides a concrete GPGPU-Sim v4.2 VM baseline useful as a sanity/reference point.

Relevant paper values:

- 4-level page table;
- page sizes: 4KB, 64KB, 2MB;
- L1 TLB for 64KB: 16 entries, 10-cycle, fully associative, per-SM;
- L2 TLB for 64KB: 512 entries per chiplet, 80-cycle, 8-way;
- page-walk queue: 256 entries per chiplet;
- page-walk cache: 128 entries per chiplet;
- 16 page walkers per chiplet.

These values are **not** the Segmentation-paper configuration. In M3 they may be used only as:

- sanity/reference values;
- a seed for a generic bring-up configuration if needed;
- evidence that finite PWQ/PWC/walker resources are reasonable to model explicitly.

If reused in M3, label them `REFERENCE_OTHER_PAPER` / `MODELING_DECISION`, never `PAPER_EXACT` for the Segmentation target.

## 4. Legacy `dev-uvm` branch

The old `origin/dev-uvm` code may be inspected for:

- queue placement/interface ideas;
- old TLB LRU code organization;
- CU-to-GMMU request routing concepts;
- same-page waiter aggregation;
- PTW-delay/wakeup plumbing.

It is a heavily diverged historical implementation and is **REFERENCE_ONLY**.

Do not wholesale cherry-pick it. Any reused concept must be re-derived against the current M1/M2 contracts and covered by current directed tests.

## 5. Current GPGPU-Sim components that are valid implementation references

At the current M2/M3 source SHAs, inspect current implementations rather than copying historical code blindly:

- `mem_access_t` / `mem_fetch` request identity and address state;
- `ldst_unit` stall/replay and memory-cycle path;
- generic cache MSHR probe/full/add/reply behavior;
- L2/memory-subpartition request/return path;
- interconnect request classes and routing;
- DRAM request/return timing;
- existing cache bypass/access-type mechanisms.

These are useful for integrating explicit PTE requests into the actual lower-memory timing path.

## 6. Generic M3 page-table backend policy

If target-paper page-table details remain unavailable at M3 entry, M3 is authorized to implement a conventional configurable multi-level/radix backend as a `MODELING_DECISION`, provided:

- the backend interface is replaceable;
- page-table levels are configurable/documented;
- PTE addresses are deterministic;
- page-table storage occupies a reserved simulated physical range;
- PTE requests are marked physical/non-recursive;
- M4B can replace/adjust the backend without rewriting TLB/MSHR/replay infrastructure.

A 4-level radix configuration is a reasonable generic default because CLAP explicitly uses four levels and the target paper does not expose a contradictory exact structure. This is still a generic project modeling decision, not evidence of the target paper's exact implementation.

## 7. M3 configuration tiers

Keep at least three configuration concepts distinct:

### `GENERIC_M3_BASELINE`

Project-defined timing baseline used to close the reusable VM infrastructure. Parameters may be chosen from current GPU-VM literature/reference values and must be labeled.

### `SEGMENTATION_PAPER_KNOWN`

Only parameters explicitly stated by the target paper, currently including:

- 64KB baseline page;
- 32-entry fully-associative L1 TLB;
- 768-entry/16-way L2 TLB;
- 16 walkers.

Unknown latency/PWC/PTW details remain unset or inherited from an explicitly labeled project model.

### `DIAGNOSTIC_IDEAL`

Ideal/unbounded translation/PWC/resource modes used only for causal upper bounds. Never treat these as hardware configurations.

## 8. Required M3 evidence boundary

M3 can claim:

- functional and timing correctness of the implemented generic VM/TLB/PTW substrate;
- PTE requests really consume intended L2/DRAM resources;
- PWC and page-size behavior in the implemented model;
- sensitivity/causality within the generic model.

M3 cannot yet claim:

- exact reproduction of the Segmentation paper's translation baseline;
- exact commercial-GPU TLB/PTW timing;
- exact sub-entry behavior;
- exact long-context synthetic-KV translation behavior.

Those claims belong to M4B/M5 after paper-specific details are resolved or explicit approximations are approved.
