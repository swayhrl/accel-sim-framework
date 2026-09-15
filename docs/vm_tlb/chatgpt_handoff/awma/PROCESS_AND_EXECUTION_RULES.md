# AWMA Process and Execution Rules

These rules are part of the project contract and are intended to improve throughput without sacrificing scientific correctness.

## 1. Prefer larger, self-contained rounds

A Codex Goal should normally combine all tightly related work needed to close one scientific/engineering boundary:

```text
inventory/audit
+ implementation
+ directed tests
+ bounded integration
+ evidence/review pack
+ handoff/report
```

Do not split trivial substeps into separate Codex rounds merely to obtain another PASS label.

## 2. Fix small non-scientific problems inline

If a problem:

- does not change scientific meaning;
- does not invalidate provenance;
- does not alter accepted raw data;
- has an obvious narrow repair;
- can be regression-tested immediately;

then Codex should repair it inside the current Goal and document the repair in the review pack.

Examples:

- typo/path normalization in newly created metadata;
- deterministic sort/order bug in a generated index;
- missing optional README link;
- schema error message quality;
- a wrapper argument mismatch with an obvious current API;
- small compatibility adapter needed for an already proven legacy field name.

Do **not** STOP and request a dedicated round for these.

## 3. Escalate only correctness-relevant uncertainties

A new decision/round is warranted when a problem affects one of:

- scientific evidence class or claim scope;
- raw-data interpretation;
- hash/provenance identity;
- capture completeness;
- simulator semantics;
- model/input identity;
- destructive migration;
- mechanism/config equivalence;
- large environment changes with uncertain consequences.

Unknown remains UNKNOWN. Codex must never invent evidence to keep moving.

## 4. Recoverable failures are sub-goals

For network, build, parser, path, storage, or environment failures:

1. diagnose;
2. try bounded safe alternatives;
3. preserve evidence;
4. continue independent work;
5. STOP only if the unresolved dependency genuinely blocks the stage acceptance criteria.

Do not treat the first failed command as a stage boundary.

## 5. Protect running experiments

Use separate worktrees/branches. Do not rebuild binaries or rewrite configs underneath a long-running experiment tied to another worktree.

## 6. No cosmetic mass migration

Do not move/rename large historical/raw trees merely because AWMA replaced C16 as the logical project name. Add metadata aliases/adapters instead.

## 7. Review-pack standard

Each substantial Goal must leave a browsable review pack containing enough evidence for ChatGPT to independently decide PASS/CONDITIONAL/FAIL. At minimum:

- README and final status;
- source anchors/branch/commit;
- changed-files/implementation summary;
- test/validation summary;
- generated schema/manifest hashes;
- open issues and scientific boundaries;
- exact paths of large external artifacts and their receipt/hash identity;
- `SHA256SUMS` over generated review files.

Large raw files remain outside Git.

## 8. Status vocabulary

Use explicit scientific/engineering status. Recommended values include:

```text
FORMAL
DIAGNOSTIC
PRE_FIX
OBSOLETE
UNKNOWN

PASS
CONDITIONAL_PASS
FAIL
BLOCKED_ENVIRONMENT
NOT_SELECTED
NOT_APPLICABLE
```

Do not collapse scientific status and execution status into one field.

## 9. Handoff ownership

- ChatGPT-owned: project decisions, next-stage specification, acceptance criteria.
- Codex-owned: implementation/report/review pack.

Codex may implement narrow obvious fixes to satisfy the handoff, but must not silently broaden claim scope.

## 10. Stop boundary for the current AWMA foundation stage

STOP only after the unified foundation review pack is complete, or after a genuine correctness/environment blocker prevents a required acceptance criterion.

Do not start new GPU capture or a production mechanism-simulation sweep in this stage.