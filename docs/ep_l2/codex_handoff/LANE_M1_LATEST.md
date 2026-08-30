# Lane M1 latest handoff

**Status:** `M1_ELASTIC_SUBSTRATE_REVIEW_READY`

The final, source-frozen M1 Elastic Substrate closeout is published at
`docs/ep_l2/review_packs/M1_ELASTIC_SUBSTRATE_r1/`. This is a
documentation-only promotion; no M1 simulator run was repeated.

Candidate provenance:

| Item | SHA |
| --- | --- |
| Framework implementation candidate / exact run source | `aae62b66685f15437cecf0193934f628e6fac6ae` |
| Core accepted parent | `878f80869ce212e779df20b6421e4dc7f987825d` |
| Core M1 frozen candidate | `955a50cbb5e8d928b6c7b0c78e1af062b835df44` |
| Runtime configuration composite | `a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416` |

Completed evidence: all ten D512 parent/M1 paired rows are exact in cycle and
instruction count, and all seven emitted CSV artifacts are byte-identical.
Source inspection, lifecycle/configuration gates, storage accounting, raw-log
hashes, and the final provenance table are included in the pack.

The formerly live `B0-Banked/FWT_7_21` and
`B0-Banked/convolutionSeparable` rows completed normally before closeout; no
simulation was rerun. The frozen candidate is approved as the parent of the
separately authorized speculative M0a+M1 integration child.

Functional mechanism bits remain off; static resident tag `i` maps to payload ID `i`; bank class remains `payload_id % 4`; no production bypass traffic exists. Unified, RO, TVD, and headroom are not implemented by M1.
