# C14 dual-path handoff

Status: `C14_DUAL_PATH_EXPLORATION_COMPLETE_READY_FOR_REVIEW`

- **P — `NO_GO_WITH_EVIDENCE`:** C12 already has Segment-before-L2 gating.
  The only speculative work before Segment resolution is the irreversible
  admission-time L1 port.  All terminal P Segment winners, including
  `16420796` on hot E/O, avoided L2, MSHR, PTW, and PTE start.  Do not build a
  duplicate gate or an unsafe local cancel path.
- **N — `GO_OBSERVATIONAL_ONLY`:** Default-off, non-perturbing telemetry now
  reports controller pending occupancy and an object/outcome-attributable
  `LOCAL_LDST_HEAD_PROXY`, plus completion-to-data-admission gap.  It is not
  global critical path or DRAM issue telemetry.
- **Exposure conclusion:** requester-latency aggregates are not GPU-stall
  cycles.  The high Decode cold pair lowers aggregate requester/local-head
  cycles by `24245368` but lowers GPU cycles by `28797`; N E/O records
  `288031809` aggregate cycles over `17581197` GPU cycles.  No speedup is
  extrapolated from a microdiagnostic.
- **C13 dependency:** final read-only fetch `9ab1e070` closes Path A and
  promotes repaired L2-mode-0 results after EQ1/EQ2; old mode-1 data remains
  superseded.  This makes N the next priority for one repaired full-ROI pair;
  P remains closed.

The complete package is
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C14_DUAL_PATH_EXPLORATION/FINAL_REPORT.md`.
