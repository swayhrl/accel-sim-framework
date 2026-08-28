---
name: decoupled-l2-experiment
description: Plan, run, monitor, or audit Decoupled-L2 Accel-Sim experiments in this repository using its external GPGPU-Sim worktree, guarded runners, manifests, and result gates. Use for Decoupled-L2 smoke, pretrace, archive, CCWS, or result-qualification tasks; do not use for unrelated Accel-Sim experiments.
---

# Decoupled-L2 experiment

Use the branch's existing execution system. This Skill is a router and evidence
gate, not another experiment runner.

## Load the applicable contract

1. Resolve the repository root and read its `AGENTS.md`.
2. Read `docs/decoupled_l2_baseline.md` before selecting or building simulator
   source.
3. Read the relevant section of `docs/decoupled_l2_runs.md` for smoke, pretrace,
   archive, resource-boundary, or result-analysis work.
4. Inspect the selected runner's `--help` and its manifest/config inputs before
   constructing a command.

The active C++ backend is intentionally in the external worktree selected by
`DECOUPLED_L2_GPGPUSIM_ROOT`. Do not edit the ignored embedded
`gpu-simulator/gpgpu-sim` checkout for this experiment. Use
`scripts/setup_decoupled_l2_env.sh` and verify the resolved source and revision.

## Respect the requested operation

- Plan or audit requests are read-only; do not start a simulation.
- For an authorized run, use the smallest existing route that answers the
  question.
- Do not infer permission for large archive extraction, full suites, parallel
  campaigns, lowered disk/RSS reserves, or cleanup from permission to run a
  smoke test.
- Check active runs and the destination state before starting or retrying work.
  Do not duplicate a live case or overwrite preserved failure evidence.

## Select an existing route

- Single backend smoke or directed overlay: `scripts/run_decoupled_l2_smoke.sh`.
- Manifest-driven public/pretrace pairs:
  `scripts/run_decoupled_l2_pretrace_cases.sh`.
- Large archive work: use the tracked planning, staging, case/batch, monitoring,
  status, and rehome scripts documented in `docs/decoupled_l2_runs.md`; preserve
  their disk, RSS, locking, reuse, and provenance behavior.
- CCWS comparison: `scripts/run_ccws_baseline.sh` and its declared trace profile.

Do not replace these paths with direct `accel-sim.out` launches unless the task
is an explicitly scoped diagnosis and the run remains disposable and recorded.

## Qualify evidence

For each run, require the route's normal-exit marker, required mechanism counter
gate, resolved configuration, executable/source provenance, and matched trace.
For paired results, confirm that baseline and proposal differ only as intended.

Report each case as qualified, incomplete, failed, or provenance/invariant
invalid. Keep diagnostic and resource-pressure runs separate from
representative performance results. Never include an unqualified case in an
aggregate or claim that Decoupled-L2 is validated from normal exit alone.

When reporting status, provide the exact run root, command or runner, source
revisions, evidence checked, remaining gaps, and the smallest safe next action.
