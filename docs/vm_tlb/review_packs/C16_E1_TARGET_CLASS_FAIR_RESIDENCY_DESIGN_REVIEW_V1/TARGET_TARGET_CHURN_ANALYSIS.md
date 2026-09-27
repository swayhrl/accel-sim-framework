# Structural target-target churn analysis

Claim boundary: structural current-policy analysis, not observed eviction.

After one full target-only qweight stream, one class can occupy 100% of B8/B16/B24 protected quota and all BFULL capacity. Every later qweight covers every target set. Conditional on later target references reaching L2 as misses and finding local protected victims, one full later stream turns the pool 4.046875× at B8, 2.023438× at B16, 1.348958× at B24, and 1× at BFULL.

Across L1-L27 before L0 reuse, the corresponding conditional turnovers are 109.265625×, 54.632812×, 36.421875×, and 27×. M1 provides no proportional-representation floor; the guaranteed old-class survival lower bound is zero. L0 survival therefore depends on filtering, hits, skipped accesses, denial, or another effect—not a fairness property of M1.

The ideal all-miss proof is stronger. L0 contributes at most 9 protected lines to any set. After L1, every set is full because both classes contribute at least 8 lines. L2 then supplies at least 8 target fills per set and M1 prefers protected victims at full quota, leaving at most one original L0 line per set. L3 supplies at least 8 more fills and removes that remainder. Thus original L0 protection is zero by the end of L3 under the stated assumptions; this is a structural proof, not a Lane4 observed-eviction result.
