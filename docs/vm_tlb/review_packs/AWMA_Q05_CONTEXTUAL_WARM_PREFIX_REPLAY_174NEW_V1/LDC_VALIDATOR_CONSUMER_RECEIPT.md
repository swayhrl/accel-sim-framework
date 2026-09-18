# LDC validator consumer receipt

The exact narrow semantic delta from `a62f5f778f97c388187b4d674b120ea131be7999` was carried forward only in `traceg_grammar_smoke.cc` and its compiled regression test. It accepts width-zero/no-address only for exact base opcode `LDC`; `ULDC` and other `LD*` remain strict. The pre-existing exact `LDGDEPBAR` exception remains intact.

174 compiled consumer tests: 22/22 PASS. The compiled smoke then accepted all 35 actual bundle traceg members. No producer, trace-parser, trace-driven, simulator binary, or F0 change occurred.
