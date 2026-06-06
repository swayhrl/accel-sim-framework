# A10 Mascar/MeDiC Gaps

A10 records real prior artifact evidence and trace-available workload intersections, but several gaps remain by design.

Known limitations:

- Prior artifact discovery is bounded and read-only. Artifacts outside `/workspace/repos` or outside the configured search root are not included.
- Workload equivalence is based on normalized benchmark names and cited source files. It does not prove paper-level experimental equivalence.
- Stats field extraction is best effort across scripts, logs, docs, configs, and CSV headers.
- A10D compares execution viability and basic GPGPU-Sim stats only. It does not reproduce Mascar or MeDiC architectural mechanisms.
- A10 does not validate NVBit tracing and does not generate new traces.

Future work:

- Pin exact prior run scripts and configs for one Mascar and one MeDiC workload.
- Build a narrow stat-equivalence matrix for fields present in both prior GPGPU-Sim artifacts and Accel-Sim logs.
- Run one workload at a time with documented config equivalence before expanding coverage.
