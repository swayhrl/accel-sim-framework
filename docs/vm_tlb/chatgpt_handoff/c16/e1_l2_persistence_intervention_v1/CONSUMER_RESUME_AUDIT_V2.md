# C16 E1 L2-Persistence Consumer Resume Audit V2

## Accepted producer

`hrl/c16-e1-l2-persistence-intervention-109-v1@4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`

## Preliminary producer audit

No producer rerun is requested.

Verified high-level producer facts:

- runtime/device capability agrees with accepted RTX4080 authority;
- exact qweight intervals are contiguous and 33,947,648 B;
- full-qweight requested set-aside is 33,947,648 B;
- runtime query-back for the full request is 37,748,736 B;
- isolated persistence positive control is large:
  - timing benefit ~35.9%
  - DRAM reduction ~61.5%;
- natural full-model target timing benefits relative to SETASIDE_ONLY are material and target-specific;
- natural target DRAM reductions do not cross the frozen 20%+4MiB material gate;
- matched unrelated persistence can reduce DRAM as much or more;
- 16 MiB is the first TESTED material timing budget; no exact threshold claim is allowed.

## Scientific contract issue that must be surfaced, not repaired post hoc

Producer decision rule:

`READY := any_material_timing AND any_target_specific`

Pre-data consumer decision rule:

`READY := exists same point: material_timing AND material_dram AND target_specific`

Because no producer primary point has material DRAM, the consumer's strict frozen rule cannot reproduce the producer's READY label.

The consumer must not change its frozen decision rule after producer data became available.

Required closure fields:

- `producer_scoped_state`
- `strict_consumer_state`
- `decision_rule_divergence = true`
- producer rule text
- frozen consumer rule text
- raw-evidence match status
- project-level authorization = REVIEW_REQUIRED

The divergence is not a raw-data contradiction.

## Raw policy receipt normalization

Real producer artifacts split policy authority across several raw records.

### Raw capability authority

`RAW_CUDA_CAPABILITY_AND_CENSUS.json`

Provides:
- runtime/driver/device identity
- L2/max-persist/max-window
- qweight census
- helper/header hashes
- qualification smoke receipt

### Per-run / per-profile authority

Raw JSON or PROFILE PASS receipt provides:
- semantic condition
- token/occurrence identity
- qweight_regions in that process
- low-level policy_receipt

Low-level policy receipt provides:
- requested_setaside_bytes
- actual_setaside_bytes
- stream_value
- access_policy_window or null
- reset_before/reset_after
- operations_before/operations_after

### Required consumer behavior

Build a normalized receipt deterministically from the raw sources.

Do not require producer to have emitted the synthetic rich schema.

Do not invent:
- set-aside alignment
- target qweight window for BASELINE/SETASIDE_ONLY
- extra API success fields not supported by raw operations

For target persistence:
- exact access window base must equal that process's target qweight data_ptr;
- num_bytes must equal exact qweight bytes;
- hit property must be persisting;
- miss property must be the recorded property;
- hitRatio must match full or partial budget contract.

For full-qweight CUDA rounding:
- preserve requested and actual query-back;
- require requested <= actual <= runtime max;
- explicitly record observed runtime rounding;
- do not reverse-engineer a universal alignment theorem.

For fixed tested partial budgets:
- observed actual must match raw query-back;
- do not assume the full-qweight rounding applies to all budgets.

For BASELINE:
- requested/actual set-aside = 0;
- no active access-policy window;
- reset/clear operations succeed.

For SETASIDE_ONLY:
- matched nonzero set-aside;
- no active target window;
- reset/clear operations succeed.

For budget sweep:
producer raw condition name is `BUDGET_L0_UP`.
Consumer may normalize it to the bounded partial-budget L0_UP policy class only after verifying:
- exact L0_UP qweight window;
- tested budget;
- full window bytes;
- hitRatio=min(1,budget/qweight_bytes);
- runtime query-back;
- reset receipts.

Every normalized receipt must retain source-file SHA(s).

## Final consumer output

Do not discard producer mechanism requirement document.

Instead verify its dimensions descriptively against evidence, while keeping its producer-scoped READY label separate from the strict consumer final state.

No GPU/NVBit/full trace/mechanism implementation is authorized by this consumer closure.
