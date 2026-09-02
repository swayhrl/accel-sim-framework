# M3-G3.1-RF — PTE Address Namespace Review Fix

## Status

**AUTHORIZED NOW.**

Independent ChatGPT review accepts the repaired M2 functional baseline at Core `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b` and Framework evidence head `c12ad7bc9fb6865e97ff8b65c215490a5d92305a`.

M2-RF is closed and accepted. The registered-waiter retry path no longer consumes/probes TLB resources while already pending, the paper-facing TLB probe counters are no longer polluted by same-waiter polling, the required observability/persistence evidence is present, and cold/integrated regressions pass.

However, the preserved provisional G3-1 commit `8c613a356e6a146951cd59c9929046c6c4cfd856` is **NOT YET ACCEPTED** because review found a concrete collision in the generic PTE-address namespace. Do not begin G3-2 until this fix passes.

## Problem

Current `radix_page_table_backend::pte_address()` derives the slot as:

```text
slot = ((page_size_class * levels + level) << vpn_bits(page_size)) | vpn
```

The shift width changes with page size:

- 64KB: `vpn_bits = 49 - 16 = 33`
- 2MB: `vpn_bits = 49 - 21 = 28`

Therefore the namespace is not globally injective over `(page-size-class, level, VPN)`.

A concrete collision exists in the current code:

```text
64KB, class=0, level=0, vpn=(4 << 28) | X
2MB,  class=1, level=0, vpn=X
```

Both generate the same slot because:

```text
64KB slot = ((0 * 4 + 0) << 33) | ((4 << 28) | X)
            = (4 << 28) | X

2MB slot  = ((1 * 4 + 0) << 28) | X
            = (4 << 28) | X
```

This violates G3-1's claimed deterministic unique PTE physical-address contract and would allow unrelated 64KB/2MB PTEs to alias before real PTE traffic is introduced.

## Required fix

Use a single fixed namespace width large enough for every supported page-size class when encoding `(class, level, VPN)`.

For the current 49-bit VA model with 64KB as the smallest supported page, the natural width is:

```text
max_vpn_bits = 49 - log2(64KB) = 33
```

A suitable mapping is:

```text
namespace_id = page_size_class * levels + level
slot = (namespace_id << max_vpn_bits) | vpn
pte_pa = pte_base + slot * PTE_BYTES
```

Equivalent injective mappings are acceptable, but they must preserve these properties:

1. no overlap between any supported `(page-size-class, level)` namespace;
2. every valid VPN for that class fits inside its namespace;
3. deterministic stable PTE address;
4. all PTE addresses remain inside the configured reserved PTE physical range;
5. application physical range remains disjoint from PTE range;
6. no change to frozen identity-like data mapping `SimPPN=SimVPN`;
7. no change to repaired M2 retry/resource semantics.

The existing `required_bytes` sizing logic already uses the maximum 64KB VPN width. Keep sizing and address encoding internally consistent.

## Required directed tests

Extend `vm_m3_g3_1_test` or add a focused test that asserts exact behavior.

At minimum:

### 1. Explicit former-collision case

Use a nontrivial `X`, for example `0x12345`:

```text
64KB key: vpn = (4 << 28) | X, level 0
2MB key:  vpn = X,             level 0
```

Assert their PTE physical addresses are different.

### 2. Namespace boundary separation

For every supported page-size class and every configured level, prove the namespace interval cannot overlap the next namespace interval. Test at least minimum and maximum valid VPN values.

### 3. Existing G3-1 contract

Retain/pass:

- same key + different level -> distinct PTE address;
- 64KB and 2MB classes -> distinct namespaces;
- PTE PA is inside reserved PTE range;
- application PA is outside reserved PTE range;
- PTE request is physical and bypasses translation;
- replacement backend seam still works;
- M2 fixed-latency translation/replay remains quiescent.

### 4. Regression

Rerun:

- M1 directed test;
- G2-1/G2-2/G2-3/G2-4;
- M2-RF pending-retry test;
- M2-RF kernel-persistence test;
- G3-1 unit test;
- cold Core+Framework build;
- one bounded functional M2 replay to ensure the G3-1 backend seam still resolves identity mapping without changing M2 behavior.

## Documentation cleanup

Update the M3 review pack so it no longer claims G3-2 is RUNNING before this review fix passes.

Correct the M2 invariant wording if touched: the current branch contains the provisional `pte_request` class, but **the M2 execution path emits no PTE memory traffic**. Do not claim that no PTE request class exists in source at the repaired head.

Update:

- `docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/G3_1_PTE_BACKEND.md`
- `docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/README.md`
- `docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`
- `docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

## Interaction with stashed G3-2 WIP

The user reports uncommitted G3-2 WIP is safely stored in Core `stash@{0}`. Do not apply or modify that stash during this G3-1 review fix. Do not use the stash as evidence.

After G3-1-RF passes, stop for ChatGPT review. G3-2 remains unauthorized until then.

## Acceptance criteria

G3-1-RF PASS requires all of:

1. PTE address mapping is injective across 64KB/2MB page-size classes and all configured levels;
2. explicit former-collision directed test passes;
3. namespace boundary tests pass;
4. reserved-range/non-recursion/replacement-backend tests pass;
5. repaired M2 regressions remain PASS;
6. one real bounded M2 replay remains clean/quiescent;
7. M3 review pack/status is corrected and complete for G3-1;
8. Core/Framework worktrees are clean and pushed;
9. no G3-2 source is committed/applied.

## STOP boundary

After closeout:

- push Core + Framework;
- report exact SHAs;
- mark G3-1-RF PASS or FAIL;
- **STOP FOR CHATGPT REVIEW**.

Do not begin real PTE L2/DRAM integration, PWC, multi-page performance work, Segmentation, synthetic KV, page fault/migration/UVM, or MCM work in this stage.
