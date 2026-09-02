# M2 IO integration hard-failure evidence

Status: `HARD_FAIL_STOP`

## Reproducible run

- Core: `3ccf4ffcb15f9456db546d2f1bab133c1e933a9c` plus an uncommitted,
  subsequently discarded IO request/response integration experiment.
- Framework: `1804d85190f64b9228322def256620784217b7a8`.
- workload: existing `vecadd` PTX binary;
- configuration: `/tmp/dtc-l1-m2-smoke-WraDhH/gpgpusim.config`, SHA256
  `8f3acf5861673e3581d9f157e6a5730d85c8a3cfd2cc468f6cd099a47a2d4610`;
- log: `/tmp/dtc-l1-m2-smoke-WraDhH/run.log`, SHA256
  `e1cff0ef5867c4806fc62f91099ec8dbfe44ba40563cb659f2f973100ecf3fe5`.

The run sets `-gpgpu_dtc_l1_mode 2` and aborts at
`baseline_cache::fill()` (`src/gpgpu-sim/gpu-cache.cc:1276`) on
`assert(e != m_extra_mf_fields.end())`.

## Cause and disposition

The attempted direct IO lower request correctly bypassed conventional L1D
MSHR allocation, but its returning response was still routed to the existing
conventional L1D fill branch. That branch requires a conventional
`m_extra_mf_fields` record and cannot accept an IO-owned request identity.

This is a source-backed M2 integration HARD failure. The experimental Core
edits were not committed and were removed after capturing the log. The pushed
Core worktree is clean at `3ccf4ffc`; Framework records this evidence only.
No M2 review pack exists, M2 is not accepted, and M3/M4/M5 must not begin.
