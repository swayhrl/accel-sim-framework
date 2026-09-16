# LDGDEPBAR frozen-consumer grammar conflict

- First raw record: 1 0 9 2 0d40 ffffffff 0 LDGDEPBAR 0 0 0
- First traceg record: 0d40 ffffffff 0 LDGDEPBAR 0 0 0
- Dynamic occurrence count: 16128.
- Route-B instrumentation packet has no NVBit MREF for this control instruction, so it retains width 0/no address.
- Frozen strict grammar result: TRACEG_GRAMMAR_REJECT: memory opcode has zero/missing width: LDGDEPBAR .
- Frozen simulator ISA maps LDGDEPBAR to ALU_OP; frozen trace-driven code treats it as an LDGSTS grouping control instruction, not an address-bearing global load.
- Frozen trace_parser.cc-only diagnostic passes the actual Q05 trace and reports LDGDEPBAR records; receipt is in evidence/ldgdepbar.

No fake address, width derived from .64, opcode rewrite, consumer change, or formal capture was performed.
