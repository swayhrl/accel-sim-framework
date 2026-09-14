# Codex Start Here — RTX3090 Campaign Closeout V0

## Branch

```text
hrl/vm-c16-g-3090-campaign-closeout-v0
```

## Required handoff

Read completely before doing any work:

```text
docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/RTX3090_CAMPAIGN_CLOSEOUT_V0/HANDOFF.md
```

## Startup instruction

Execute **V0 only** from the handoff.

Primary objective:

> Inventory, classify, hash, reconcile provenance, and prepare a non-destructive curation plan for the completed RTX3090 C16 Route-B campaign.

Hard constraints:

```text
NO GPU execution.
NO Llama execution.
NO Q1/Q2/Route-A rerun.
NO CUTLASS identity repair.
NO representative canary.
NO formal capture.
NO RTX4080 evidence mixed into RTX3090 authority.
NO deletion/move/rename/compression/rewrite of existing evidence.
NO authority reinterpretation or denominator change.
```

Before changing files:

1. verify branch and lineage;
2. inspect `git status`;
3. read `HANDOFF.md` completely;
4. inspect the frozen authority documents referenced by the handoff;
5. inventory first, write reports second.

Allowed changes are limited to new CPU-only helper scripts and new V0 closeout reports/docs.

Required output directory:

```text
docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/RTX3090_CAMPAIGN_CLOSEOUT_V0/V0_INVENTORY/
```

Do not proceed to physical curation after producing the V0 reports. Commit and push V0, then stop and report for review.

If local/archive evidence expected by the authority is not accessible, record it as missing/external-only; do not fabricate or regenerate it.
