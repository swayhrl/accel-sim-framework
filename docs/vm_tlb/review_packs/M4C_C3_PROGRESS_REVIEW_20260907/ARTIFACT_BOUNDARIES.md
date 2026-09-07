# Artifact boundaries

Included:

- this docs-only review snapshot;
- immutable source, binary, config, object-map, and kernel-list hashes;
- per-arm terminal or in-progress counts derived from existing manifests and
  logs;
- the frozen telemetry interpretation and validation boundary.

Excluded:

- `/workspace/m4c-c3-formal-20260905-v1` scratch;
- raw `run.log` files, traces, trace archives, and SQLite locality databases;
- all C3 configurations, kernels lists, and object maps;
- Core implementation changes and simulator binaries.

Consequently this branch cannot alter behavior, replay results, or the C3
supervisor's source-anchor checks.
