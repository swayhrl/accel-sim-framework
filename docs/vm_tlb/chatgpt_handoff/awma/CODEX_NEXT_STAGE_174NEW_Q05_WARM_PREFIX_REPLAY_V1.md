# CODEX NEXT STAGE — 174-new Q05 Warm Prefix Replay V1

Status: ACTIVE MAINLINE / may WAIT for 109 context bundle.

Stage:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1`

Node: 174-new / port 2239.

## Start point

Read coordination branch:

`hrl/awma-q05-contiguous-prefix-warm-replay-handoff-v1`

Read:

- `CURRENT_STATE.md`
- `DISCUSSION_REFERENCE.md`
- `Q05_CONTIGUOUS_PREFIX_CAPTURE_CONTRACT_V1.md`
- `CODEX_NEXT_STAGE.md`

Execution parent:

```text
hrl/awma-q05-warm-replay-feasibility-174new-v1
e2fa35f045e0b4f977a964d9c92974c9f6d3e240
```

Recommended branch:

`hrl/awma-q05-warm-prefix-replay-174new-v1`

## Objective

Consume the future formal same-run launches0..34 context bundle and measure Q05 after real predecessor suffixes while preserving accepted F0 kernel-boundary semantics.

No new mechanism experiments.

## B0 — Feasibility V1.1 semantic closure

Before interpreting any warm result, close gaps left intentionally/implicitly by V1:

1. Separate L1 TLB and L2 TLB kernel-boundary behavior.
2. Record actual F0 `flush_l1` and `flush_l2` values and resulting L1/L2 data-cache behavior.
3. Record PWC behavior separately.
4. Confirm translation MSHR/PWQ/walker quiescence/drain at kernel completion.
5. State explicitly that the previous self-warm cycle reduction is a combined modeled warm-state effect; do not attribute it solely to translation.
6. Preserve the 228-offline-VPN vs 240-simulator-key mismatch as different identity domains unless a same-scope reconciliation is actually proven.

Output:

- `F0_KERNEL_BOUNDARY_STATE_MATRIX_V1_1.tsv`
- `SELF_WARM_INTERPRETATION_V1_1.md`

## B1 — Prepare context-bundle consumer

Implement/qualify an ordered multi-kernel consumer that:

- reads the 109 context-bundle manifest;
- verifies all 35 member hashes;
- verifies exact ordered sequence and same-run address context;
- rejects missing/interior/duplicate members;
- re-runs frozen trace validator as needed;
- constructs fresh-row kernel sequences for P1/P2/P4/P8/P16/P34.

Do not concatenate independent-run traces.

If 109 bundle is not yet durable+ACK, finish B0/B1 tooling and close as:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_WAITING_FOR_CONTEXT_BUNDLE`

Do not invent the bundle.

## B2 — Formal contextual input identity

After consumer verification, create a new context-input identity distinct from the old isolated single-kernel SIM_INPUT.

This identity must hash:

- source context bundle;
- ordered selected prefix row definition;
- accepted framework/core/config anchors;
- address-context contract;
- measurement-boundary contract.

Do not mutate or supersede the old Q05 SIM_INPUT.

## B3 — Replay matrix

Run each row from a fresh simulator process/state:

```text
ISOLATED_Q05  = accepted baseline reference
P1  + Q05
P2  + Q05
P4  + Q05
P8  + Q05
P16 + Q05
P34 + Q05
```

For each warm row:

- execute predecessor suffix in exact order;
- preserve accepted modeled state across kernel dispatch;
- snapshot monotonic counters immediately before Q05;
- run Q05;
- snapshot after Q05;
- use after-before for target-only metrics.

Never call a state-reset API at Q05 entry.

## B4 — Required Q05-only measurements

Report at least:

- Q05 cycles;
- completed active thread-instructions;
- L1 TLB access/hit/miss;
- L2 TLB access/hit/miss;
- translation MSHR alloc/merge/full/HWM;
- walks;
- PWC;
- PTE traffic and L2/DRAM split;
- requester-latency decomposition;
- L2 data-cache and DRAM traffic in source-defined units.

Where source-safe, record the first Q05 translation outcome by simulator key `{asid,vpn,page_size}` to distinguish keys already warm at Q05 entry from keys requiring a new walk.

Any new diagnostic logging must be disabled by default and pass isolated-Q05 neutrality before use.

## B5 — Compare with native page overlap

Join only at the level justified by identity.

Allowed:

- compare trend of P1/P2/... trace-page overlap versus Q05 walk/miss reduction;
- compare 4KiB and 64KiB native overlap curves separately.

Not allowed:

- equating native VPN overlap directly with exact simulator resident-key count;
- forcing 228 and 240 into a fabricated 1:1 mapping.

## B6 — Scientific decision

Answer quantitatively:

1. Does real predecessor context change Q05 total cycles versus isolated replay?
2. How does prefix length affect Q05 L1/L2 TLB hits/misses and walk count?
3. At what prefix length do translation metrics and total cycles stabilize, if they do?
4. How much of the observed context effect is clearly translation-related, and what portion remains mixed with L2 data-cache warming?
5. Is the original isolated-Q05 characterization still representative enough for mechanism work, or must future Q05 studies use a contextual prefix?
6. Which prefix length should become the future accepted Q05 context baseline?

Do not start a mechanism based on the answer.

## Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_WARM_PREFIX_REPLAY_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1/`

At minimum:

- README.md
- SOURCE_ANCHORS.md
- F0_KERNEL_BOUNDARY_STATE_MATRIX_V1_1.tsv
- SELF_WARM_INTERPRETATION_V1_1.md
- CONTEXT_BUNDLE_CONSUMER_RECEIPT.json
- CONTEXT_INPUT_IDENTITY.json
- WARM_PREFIX_RESULTS.tsv
- Q05_TRANSLATION_RESULTS.tsv
- Q05_DATA_CACHE_RESULTS.tsv
- Q05_FIRST_KEY_OUTCOMES.tsv when source-safe
- NATIVE_OVERLAP_VS_SIM_TRANSLATION.tsv
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Expected complete marker:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_COMPLETE_WITH_SCOPE`

If waiting for 109 only:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_WAITING_FOR_CONTEXT_BUNDLE`

Commit, push, remote verify, clean worktree and STOP.
