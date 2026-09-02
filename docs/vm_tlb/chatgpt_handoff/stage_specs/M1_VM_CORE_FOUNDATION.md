# M1 — VM Core Foundation

## Objective

Establish the minimum reusable VM substrate and prove that inserting the VM framework does not perturb the frozen simulator baseline when translation is disabled or ideal/identity-mapped.

M1 is not a TLB/PTW implementation stage.

## Authorized scope

- define and document SimVA/SimPA contracts;
- add minimal request/address state needed to preserve both identities;
- add configurable VM enable/disable and ideal-translation modes;
- add a deterministic identity-like page mapper;
- establish the translation insertion point between coalesced memory transactions and the real data-cache access;
- add observability and assertions required for transparency/invariants;
- create long-lived VM specification/validation documents;
- add directed microtests needed to prove the contract.

## Explicitly forbidden

- functional L1/L2 TLB lookup/replacement;
- translation MSHR;
- page-walk queue/walkers/PWC;
- PTE memory traffic;
- page faults/migration/UVM;
- segmentation/sub-entry implementation;
- TLS/MCM behavior;
- performance characterization beyond transparency validation.

## M1.1 — Freeze semantic specification

Create/update long-lived documents under `docs/vm_tlb/specs/`:

- `VM_CORE_SPEC.md`
- `VM_PIPELINE.md`
- `VM_VALIDATION_MATRIX.md`

The specification must define:

- `TraceAddr -> SimVA -> SimPA` naming;
- identity-like page mapping semantics;
- page offset and base-page calculations;
- preservation of both SimVA and SimPA;
- what request types are in v0 scope;
- insertion point relative to coalescing/L1D;
- kernel/context lifetime semantics;
- disabled/ideal modes;
- future extension boundary for page-table/TLB/MCM backends.

If code inspection shows a materially safer insertion point than the expected post-coalescing/pre-L1D location, document evidence and STOP before changing the approved semantic placement.

## M1.2 — Scaffold and mapper

Implement the minimum configuration and state plumbing.

Required logical modes:

- `VM_DISABLED`
- `VM_IDEAL_IDENTITY`
- future functional translation mode placeholder only if needed structurally

Identity mapping must preserve the data address numerically for the baseline mapping:

`SimPPN = SimVPN` and data `SimPA == SimVA`.

Do not overwrite the only copy of SimVA. Downstream cache/DRAM uses the translated data address when VM is enabled; observability can recover both.

## M1.3 — Transaction-boundary proof

Prove with source reasoning plus directed tests whether one generated `mem_access_t` can cross the chosen base-page boundary.

Expected base page for bring-up: 64KB.

If no crossing is possible under existing alignment/transaction rules, encode a validation assertion/check. If crossing is possible, implement the minimal correct transaction split before later TLB work and document it.

Do not implement per-lane TLB behavior as a workaround.

## M1.4 — Transparency validation

Run the frozen baseline and the new modes on at least:

1. the bootstrap Rodinia LUD-64 / QV100 trace;
2. the same trace with unchanged SM86 RTX3070 config;
3. one additional memory-intensive trace if readily available from existing short-test inputs.

For each trace compare:

### A. VM disabled vs frozen baseline

Must match for:

- simulated instruction count;
- cycle count;
- IPC;
- L1D access/miss counts;
- L2 access/miss counts;
- DRAM read/write request counts;
- architecturally relevant request counts available in the baseline.

### B. VM ideal + identity vs VM disabled

Must match the same non-VM outcomes. VM-only lookup counters may differ only as explicitly specified; ideal mode must not add latency or queuing.

If a baseline statistic is nondeterministic in the unmodified simulator, prove that independently before accepting tolerance. Do not invent tolerances without evidence.

## Required directed tests

At minimum:

- address preservation: SimVA retained after translation;
- page offset preservation;
- identity mapper returns exactly the original data address;
- VM-disabled path bypasses all VM latency/state effects;
- ideal identity path returns before L1D with zero added timing effect;
- request type classification remains unchanged;
- transaction/page-boundary assertion or split test.

Prefer machine-checkable expected outputs rather than grep-only PASS messages.

## Required observability

At M1 closeout, provide enough structured output to prove:

- number of requests entering the VM hook;
- number bypassed because VM disabled;
- number ideal-translated;
- SimVA/SimPA equality in identity mode;
- zero translation-caused stall cycles in disabled/ideal modes.

## Acceptance criteria

M1 PASS requires all of the following:

1. specification documents match implementation;
2. both SimVA and SimPA are preserved/observable;
3. identity mapping is deterministic;
4. VM-disabled transparency passes;
5. ideal+identity transparency passes;
6. transaction/page-boundary behavior is proved and tested;
7. no functional TLB/PTW has been smuggled into M1;
8. clean build, relevant directed tests, `git diff --check`, provenance capture pass;
9. no correctness invariant violation.

Any transparency failure is a hard STOP before M2.

## Deliverables

Review pack:
`docs/vm_tlb/review_packs/M1_VM_CORE_FOUNDATION/`

Include machine-readable comparison table for transparency runs and exact source/config/trace SHAs.

If PASS, Codex may proceed directly to M2.
