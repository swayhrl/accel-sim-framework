# Latest diagnostic binary all-OFF equivalence

This supplement adds one actual full-application vectorAdd_4M legacy all-OFF
control to FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2. Both source identities and
binary hashes are explicit. Scientific configs, trace, environment, vectors,
epoch and terminal contract match. Cycles/instructions and all seven parsed
CSV families are exact; raw logs and parser bytes are bound by SHA256.

The candidate includes Lane1 runtime-ready parent 126394be plus the Lane4
ideal changes, with all ideal bits OFF and finite-WBUF mode OFF. This verifies
legacy behavior on this application only. It is not a new B16 performance
baseline, an independent shared-release qualification, or numeric SASS output
validation. Formal diagnostic cells still require Lane1 common integration
and Lane5 same-binary release qualification/baseline specs.
