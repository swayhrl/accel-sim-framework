# Retry570 NVBit engineering unblock qualification

Status: `NVBIT_RETRY570_V175_ENGINEERING_UNBLOCK_QUALIFIED` (diagnostic/engineering only).

The prior root cause remains `NVBIT_CORE_MODULE_BOOKKEEPING_PATHOLOGY_CONFIRMED`.
The unique NVBit 1.8 EMPTY+EAGER first-use window reached CUDA init and input
preparation but not `READY` in 60.660996s.
Consequently `process_to_ready_s`, `round1_s`, and `round2_s` are absent, and
one-time versus repeated behavior is **not determined** for 1.8. Its failed
run remains in the budget ledger; a later source-only fix corrected an invalid
classification name without rerunning the GPU window.

With GPU, driver, CUDA, torch, libtorch and exact reproducer held fixed, NVBit
1.7.5 passed official `instr_count_bb + vectoradd`, then its EMPTY exact
reproducer completed in 5.677317s. The requested
LAZY setting was overridden by the vendor version: banner and CUDA query both
show EAGER. This caveat is preserved rather than calling the observed modes
identical. The contrast remains version-sensitive because the independent 1.8
EAGER window did not reach READY.

The normal Lane G C16 tracer rebuilt against frozen NVBit 1.7.5 then completed
one EAGER C2 tensor-fill first-kernel smoke. Submission was at
5.630197s and completion at
5.872201s; total target and
remote transaction wall were 6.655896s and
6.759123s. An impossible dynamic
range kept tracing inactive: the post-run scan found zero `.trace`/`.trace.xz`
files. This qualifies a minimal engineering path, not any model or capture.

Recommended unblock: pin exact NVBit 1.7.5 archive/core/tool hashes, use EAGER,
perform a bounded zero-trace prewarm outside `MEASUREMENT_ACTIVE`, emit READY
only after terminal/identity/zero-trace/process-cleanup checks, and create the
measurement gate afterward. Any future model/capture still needs explicit
authorization and model-level correctness/identity requalification.

All 25 retained remote payloads plus the final execution ledger are locally
SHA-closed. `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`, active GPU and diagnostic
process counts are zero, and no measurement marker remains. No model, Llama,
Qwen, trace, scientific capture, C target, 300-second watch, or 6+6 rerun was
performed.
