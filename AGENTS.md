# Accel-Sim architecture research

## Scope and authorization

- Follow the user's requested stage. Analysis, review, mapping, and planning are
  read-only unless the user separately asks for implementation.
- Do not launch a long simulation, full trace campaign, large download, or
  destructive cleanup unless the request clearly authorizes that operation.
- Preserve unrelated changes, incomplete runs, failure artifacts, traces, and
  archives. Treat them as user-owned evidence.

## Resolve the active simulator first

- Identify the current worktree, branch, repository root, and relevant execution
  contract before choosing source files or commands.
- Do not assume `gpu-simulator/gpgpu-sim` is the active GPGPU-Sim source. Some
  experiments intentionally build an external GPGPU-Sim worktree. Follow the
  branch setup script and verify the resolved `GPGPUSIM_ROOT` before editing or
  building.
- When Accel-Sim and GPGPU-Sim are separate repositories, record and reason
  about both revisions and dirty states.

## Reuse the repository workflow

- Read the relevant document under `docs/`, experiment manifest, and existing
  runner before inventing a command or helper.
- Prefer tracked runners for build, smoke, paired experiments, resource guards,
  provenance, monitoring, and finalization. Add automation only when an actual
  gap remains; do not duplicate an existing runner inside a Skill.
- Keep paper claims, simulator observations, inferred behavior, and modeling
  choices distinguishable.

## Architecture changes

Before changing modeled behavior, establish the affected request lifecycle,
architectural state, timing, resource contention, ordering/backpressure,
configuration, statistics, and validation invariants. Preserve a default-off or
baseline path when the mechanism permits it.

Use validation proportional to the change:

1. Read-only work: cite current code/config/result evidence; do not build merely
   to complete a checklist.
2. Local code change: build the affected target and run the smallest relevant
   smoke or directed test.
3. Mechanism change: compare matched baseline/proposal runs and check mechanism
   counters plus request/transaction invariants.
4. Performance or paper claim: use the declared workload matrix, provenance
   gates, and strict finalizer for that experiment.

Do not claim completion from compilation alone, from a normal simulator exit
alone, or from one favorable IPC result.

## Experiment evidence

- Keep diagnostic, mechanism-coverage, representative-performance, and full
  paper runs separate.
- Prefer run-local immutable evidence: executable identity/hash, source
  revision, resolved configuration, trace/workload identity, launch command,
  full output, and derived statistics.
- Compare results only when their intended differences are explicit. Exclude
  missing, partial, failed, provenance-mismatched, or invariant-failing runs
  from aggregates and completion claims.
