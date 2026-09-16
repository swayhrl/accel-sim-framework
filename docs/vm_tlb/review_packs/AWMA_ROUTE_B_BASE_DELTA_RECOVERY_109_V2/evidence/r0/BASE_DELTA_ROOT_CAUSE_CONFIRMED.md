# BASE_DELTA_ROOT_CAUSE_CONFIRMED

Mode-2 fixture record: 0000 00000005 0 LDG.E.32 0 4 2 1000 64 0

- Effective active lanes: 2 (mask 0x5).
- Producer v5 base_delta encoding: base 0x1000 + one delta 64 + immediate 0.
- Encoded delta count: 1 = active_lanes - 1.
- Frozen parser expectation: 2 deltas, so it consumes immediate 0 as a second delta then reports missing immediate.
- Frozen parser mode-2 return code: 2; stderr: TRACEG_GRAMMAR_REJECT: missing immediate .

ULDC fixture record: 0030 ffffffff 0 ULDC.64 0 0 0

- It remains a width-0/non-MREF record.
- Frozen parser ULDC return code: 0; stdout: {"status":"TRACEG_GRAMMAR_PASS","trace_version":5,"thread_blocks":1,"instructions":1,"opcode_counts":{"ULDC.64":1}} .
