# L2 deterministic `LDC.U8` grammar audit

Decision: **L2_GRAMMAR_REPAIRED_DETERMINISTIC**.

This is engineering enablement, not a translation mechanism. The original
blocked artifact is unchanged.

## Producer record

All 256 L2 occurrences have the exact trace-v5 form:

`PC MASK 1 R0 LDC.U8 0 0 0`

The fields after the opcode are zero source registers, serialized memory width
zero, and immediate zero. There is no dynamic-address payload to recover.
Opcode suffix `U8` deterministically denotes one byte at the SASS level, but it
does not imply a missing list of lane addresses.

## Accepted consumer semantics

The current strict grammar consumer has a deliberately exact exception only
for base opcode `LDC`:

- `implicit_constant_load_opcode(opcode)` is true only when
  `base_opcode(opcode) == "LDC"`;
- width-zero address-bearing `LDG`, `LDGSTS`, and other `LD*` remain rejected;
- Ampere opcode mapping classifies `LDC` as `OP_LDC/ALU_OP`;
- trace-driven execution applies the existing deterministic `OP_LDC`
  constant-space approximation and does not treat the record as a global VM
  request.

No address, opcode, instruction, mask, CTA/warp, UID, or scheduling record is
synthesized.

## Known-good canary

Accepted strong-baseline SPLITKV trace
`kernel-17543-ctx_0x5be0856adcb0.traceg.xz` contains 504 `LDC.U8` records in the
identical `width=0; immediate=0` form. It previously passed full simulation and
correctness/quiescence under the same binary family.

The freshly compiled strict consumer reports:

- L2: `TRACEG_GRAMMAR_PASS`, 64 thread blocks, 674,715 instructions,
  `LDC.U8=256`;
- SPLITKV canary: `TRACEG_GRAMMAR_PASS`, 126 thread blocks, 1,320,771
  instructions, `LDC.U8=504`.

## Derived authority

The derived `.traceg.xz` is a byte-identical copy:

- original SHA-256:
  `db391d6731d0568a0abf0283546c564d793adc0fbeecab7010831eb8329297e6`;
- derived SHA-256: identical;
- modified instruction records: `0`;
- consumer-semantic normalization records: `256`.

The normalization is therefore provenance/consumer qualification, not trace
rewriting. The original Native artifact stays in place and retains its original
109 receipt.

## Scope boundary

This audit does not claim exact real-hardware constant-cache timing or repair
the historical `OP_LDC` approximation. It proves only that the L2 input is
deterministically consumable under the same accepted semantics already used by
a known-good simulated trace, with no effect on global virtual-memory requests.
