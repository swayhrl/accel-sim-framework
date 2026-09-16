# AWMA 174-new LDGDEPBAR consumer-validator hotfix report

Status: `174NEW_SIM_CONSUMER_LDGDEPBAR_VALIDATOR_HOTFIX_PASS`

Starting coordination authority was `67c9f916dfc7211ed2d931ff4cd1cf0c5bdd889b`; accepted consumer base remains `25aa29862239a408099639ae9d5f1a0ea4fee1e1`.

The strict validator now exempts only exact `LDGDEPBAR` from lexical `LD*` address-bearing classification. This matches Ampere ISA `ALU_OP` and trace-driven LDGSTS grouping semantics. No producer, frozen parser, simulator binary, Q05 workload/target, or baseline identity was modified.

The real compiled grammar-smoke fixture gates passed: LDGDEPBAR width0/no-address PASS; LDG.E.32 width0 FAIL; LDGSTS width0 FAIL; valid memory PASS; malformed width/address FAIL. The full consumer test suite passed 21 tests, retaining all pre-existing 16 tests.

No SIM_INPUT_ID was issued and no 10k replay was run. The frozen mode-2 base-delta limitation remains outside this hotfix. Node109 may now fetch this exact source for its Q05 R3 parser cross-check and formal producer closure.