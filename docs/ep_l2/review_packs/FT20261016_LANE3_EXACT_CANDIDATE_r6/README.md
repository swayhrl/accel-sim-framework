# Lane 3 r6 — exact Lane 1 candidate static adaptation

Authority: coordination77a9fbe937ea23465cf0d0076d2df1909f52d055, reading review_r4/PARALLEL_CONTINUE.md then review_r5/CONTINUE.md. This continues the same Lane 3 branch and worktree. Lightweight source adaptation and audits are completed without waiting for Storage-Ops; the production build/application admission policy is unchanged.

Exact target: Lane 1 uncompiled candidate62dc1d179b5516e68b21b695c7a9c5d0667e9671, published at Corec93d900e1f968a3b69990dc29b78d50fc18f35ac. Their full Git trees are equal23f407cfadc7728b50f6f91177319ada4029cd2b. Lane 3 adapted Coredfd9d5459f189d4d85a0ff33fc83ed7a75fc3ba2; Framework audit sourcead7da27ea698232c6e851a76bed2a527dcfcfdae. This is a precise source candidate, not a compiled/qualified official R0.1 or RO release.

The new Lane 1 partition caller invokes ft_try_force_tag_access directly. RO's prior wrapper-only prefill guard could be bypassed through that new entry. The adaptation adds a nonmutating epoch guard to the try entry, retains the wrapper guard, and performs the existing Tag-generation/owner handshake only after successful common prefill. It preserves Lane 1's dirty/pending/pin/WAD/allocator refusals and exact physical clock, partition closure and full-width/partial-copy implementations.

Executed:28 source checks; eight Python audit-tool tests (including missing/late guard, dirty-gate, offset-clock, detached-install and descriptor-capacity negative cases); four isolated-index patch checks; exact full-tree reconstruction from both the candidate and its tree-equivalent publication. All are STATIC/TOOL evidence. No C++ compiler, production binary, four-mode qualification or application simulation was run. No unchanged oracle certification, old calibration, r4 module suite or r5 config suite was rerun.

Minimal source and test patches apply to the precise Lane 1 candidate. CONFLICTS.json records the four actual merge conflicts and resolutions; PATCH_AND_TREE_CHECKS.json records exact parent/source/tree identities. SOURCE_AND_GATES.json distinguishes completed low-resource work from still-unexecuted production validation. Lane 1 retains the unique R0.1 build; Lane 5 retains independent acceptance and formal runs.

All old r1–r5 packs, five oracle inputs and withdrawn R0/R1 raw/binaries remain unchanged. FWT's empty whole-commandlist certificate stays valid negative coverage; closed-world scope and budgets remain fixed. No Ops transfer/deletion, DTC-L1 process/data/quota mutation, new worker or build lease was performed.
