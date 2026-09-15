# C16 V5 — LDGSTS capture qualification

## Objective

Extend the existing C16 formal capture method from direct `GLOBAL + MREF` instructions to the address-bearing `LDGSTS...` global-to-shared path without weakening provenance or replay semantics.

## Static classification

For every audited target function, classify special rows as:

- `SPECIAL_GLOBAL_ADDRESS_PATH`: address-bearing global traffic such as `LDGSTS...`;
- `SPECIAL_MEMORY_CONTROL`: dependency/control instructions such as `LDGDEPBAR` that do not themselves carry a global address;
- `SEMANTICS_UNRESOLVED`: insufficient evidence.

Do not count `LDGDEPBAR` as a memory address event.

## Operand qualification

`LDGSTS` has distinct shared-destination and global-source semantics. Before formal capture, determine which NVBit MREF operand corresponds to the global source.

Qualification must use the exact SM89 instruction metadata and a bounded canary. Do not assume operand position from SASS text alone.

For one representative executed `LDGSTS` row:

1. enumerate the instruction's MREF operands and operand indices;
2. instrument candidate MREF operands separately;
3. record exact addresses with terminal closure and zero overflow;
4. bind the canary to a same-process `C16_ADDRESS_CONTEXT_V1`;
5. identify the global-source operand using convergent evidence from NVBit operand metadata, SASS semantics, and runtime address-space/range evidence;
6. reject ambiguous qualification fail-closed.

The shared-destination operand must never be promoted as a GPU global VA.

## Formal special-path evidence

After operand qualification, freeze the exact static `LDGSTS` set for a selected function/code object and replay one static row per deterministic run, analogous to direct MREF sharding.

Each shard must carry:

- target/function/code-object identity;
- function-local occurrence;
- static instruction index;
- exact opcode/SASS;
- selected MREF operand index;
- `path_kind=LDGSTS_GLOBAL_SOURCE`;
- trace binary hash;
- terminal status;
- callback/warp/address counts;
- overflow/drop counts;
- same-process address-context hash;
- static-set hash.

A selected row with zero execution is valid only when exact replay, terminal-complete and zero overflow/drop prove `ZERO_EXECUTION_PROVEN`.

## Binary format

Prefer reusing the already qualified C16WARP record layout if no binary schema change is required. Bind operand index and path kind in the hash-closed shard/logical manifest.

If the existing binary format cannot unambiguously represent the special path, introduce a versioned format rather than silently overloading fields. Any new format requires round-trip decoder tests before formal admission.

## Width and access kind

For `LDGSTS...128`, global-source access width may be classified as 16B only when the exact SASS/static row contains the explicit `.128` width and the decoder cross-checks it. The global-source access kind is `READ`.

Otherwise preserve unknown width.

## Coverage labels

For a target with direct and special paths:

- direct evidence retains `DIRECT_GLOBAL_MREF_COMPLETE_SET`;
- special evidence becomes `LDGSTS_GLOBAL_SOURCE_COMPLETE_SET` when its frozen static set is closed;
- target-level set coverage may become `ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL` only when both are closed and no unresolved address-bearing path remains.

This label does **not** imply one ordered whole-kernel trace.

## Unsupported claims

Even after set-level coverage passes, prohibit:

- cross-direct/special temporal order;
- cross-shard reuse distance;
- single-run whole-kernel physical absolute-VA footprint;
- absolute-VA union across replay address spaces.

Per-shard object attribution is allowed only with same-process address context. Cross-replay comparison should use semantic/object-relative normalization where independently proven.
