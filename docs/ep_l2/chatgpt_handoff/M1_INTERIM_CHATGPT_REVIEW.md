# EP-L2 M1 Interim ChatGPT Review

Date: 2026-08-30

Review status: **PASS FOR SPECULATIVE INTEGRATION**.

This review accepts the frozen M1 implementation candidate as the preferred integration parent. A final M1 closeout pack/status is still required for administrative `M1_FINAL_PASS`, but no remaining simulator run is currently required by the reviewed evidence.

## Frozen candidate

```text
Parent Core       878f80869ce212e779df20b6421e4dc7f987825d
M1 Core           955a50cbb5e8d928b6c7b0c78e1af062b835df44
Framework runtime aae62b66685f15437cecf0193934f628e6fac6ae
runtime config    a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

M1 is exactly one Core commit over the accepted D512 parent. No Framework implementation delta is required for the recorded M1 runs.

## Parent equivalence — PASS

All required workloads are now complete for both B0 variants:

```text
vectorAdd_4M
convolutionSeparable
cfd_097k
sad
FWT_7_21

x {B0-Legacy, B0-Banked} = 10 pairs
```

Every pair has exact cycles and instructions and all seven existing parsed artifacts are byte-identical:

```text
target_summary
target_slice
target_kernel
target_bank
target_window
target_l1
target_dram
```

This is strong evidence that the M1 global payload namespace/handle/tag-sidecar refactor preserves the accepted static D512 behavior.

## Source / correctness review — PASS for integration

The source implements the intended infrastructure-only delta:

- one 1152-slot physical payload namespace;
- explicit `{payload_id,generation}` handle;
- role/owner/generation state;
- tag-index -> payload-handle sidecar;
- static resident mapping remains `tag_index i -> payload_id i`;
- bank identity remains `payload_id % 4`;
- production bypass traffic remains absent;
- speculative rollback restores both slot and sidecar;
- fill validates handle/owner/generation before accepting returned data;
- functional feature bits are default OFF and unsupported requested features fail closed.

Directed payload-store, payload-banked, WAD, descriptor/MSHR integration, schema, and mode-switch tests pass after a Release build.

## Final M1 packaging items

Before administrative `M1_FINAL_PASS`:

1. publish the final `M1_ELASTIC_SUBSTRATE_r1/` pack rather than leaving only the interim-named pack;
2. record the final implementation Core SHA and exact static parent equivalence set;
3. quantify sidecar/role metadata separately from the fixed 1152x128B data budget;
4. preserve `git diff --check` / clean worktree evidence;
5. for future integrated runners, record explicit `experiment_mode` / functional feature vector in every manifest rather than inferring the default-OFF mode only from unchanged config text.

These are packaging/provenance requirements, not reasons to rerun the ten accepted M1 pairs.

## Decision

M1 Core `955a50cbb5e8d928b6c7b0c78e1af062b835df44` is **approved as the base of the speculative M0a+M1 integration child**.

The integration child remains `SPECULATIVE_PENDING_GATE` until the administrative `M1_FINAL_PASS` and the still-pending `M0A_FINAL_PASS` are both published.
