# C12 operator-aware mechanism deep-dive provenance

- Formal C12 source commit: `a268aba0d01310294074ded5bb8017e2092394c0` (`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`, 22/22 terminal PASS).
- Analysis branch input: accepted operator-aware final-review commit `247f11a9c52174d3294e701fca38a7e2aaa00dba`.
- Read-only inputs: 22 immutable `run.log` / `C12_ARM_VALIDATION.json` pairs, accepted 692/740 operator map, and existing trace-scan TSVs.
- No `accel-sim.out`, simulator replay, or trace scanner was invoked. No formal C12 asset was modified.
- Scope contract: lane references are not cache transactions; KERNEL-scope cache records are not TLB accesses; FULL_ROI_ONLY and FIXED_WINDOW_PARTIAL records are not apportioned to kernels.
