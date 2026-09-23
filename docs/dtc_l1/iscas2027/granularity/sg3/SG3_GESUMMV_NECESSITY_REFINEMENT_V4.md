# SG3 GESUMMV V4 necessity refinement

This V4 table preserves the V3 plan and records an explicit user-authorized
parallel exception to the former A1-before-A2 launch order. It authorizes only
the two fresh baseline retries and cap=512/cap=2048 IO/OO rows. It does not
authorize GESUMMV capacity or MSHR sweeps, new parameter points, changed
identities, reuse of historical unvalidated cells, or result-dependent point
selection.

All six rows receive fresh UUID attempts and row-local strict validation on
terminal state. The original exit -9 attempts remain immutable non-scientific
failures.
