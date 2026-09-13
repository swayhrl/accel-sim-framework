# Retry570 PyTorch/NVBit first-kernel stage diagnostic

Status: `NVBIT_PYTORCH_FIRST_KERNEL_STAGE_DIAGNOSTIC_COMPLETE`.

This is a bounded diagnostic-only C0--C4 matrix: no trace, model, Llama,
Qwen, C target, or scientific timing/capture was run. All ten independent
processes completed before their fixed 60-second wall limit. The old 300-second
one-shot watch remains closed and was not rerun.

The minimal reproducible slow case is `C4_SMALL_GEMM_LIBRARY_KERNEL`. Its first
launch was `_ZN7cutlass7Kernel2I65cutlass_80_wmma_tensorop_f16_s161616gemm_f16_16x16_32x1_nn_align8EEvNT_6ParamsE`. NVBit reported 89 related
functions and enumerated 88 distinct functions through `nvbit_get_instrs()`.
That instruction-discovery stage took 19.969523
seconds for 66032 total static instructions;
insertion took 0.000003 seconds, enable took
0.059192 seconds, and launch-return through synchronized
completion took 0.006221 seconds.
The complete C4 probe duration was 20.041227 seconds and
the PyTorch child completed at 23.064094 seconds.

By contrast, C3's single-related-function add kernel completed NVBit discovery
in 0.231030 seconds and its full probe in
0.239395 seconds. C2/C3/C4 all emitted launch,
instruction-discovery, insertion, enable, and synchronization markers.

The C4 five-second snapshots saw a live GPU-attached process, advancing
`GET_INSTRS` markers and host CPU samples of 97.8%, 53.8%, 37.2%, and 28.5%.
The main thread's `wchan` was `do_wait`, consistent with a child-process wait
during tool-side instruction discovery; most other threads were in futex wait.
The node denied `/proc/.../stack` reads even as root, so the retained evidence
uses non-destructive `wchan` and syscall snapshots rather than claiming a
symbolized native stack.

Conclusion: this supports B, an NVBit related-function/static-instruction
discovery expansion in the GEMM library universe. It does not support a
deadlock (D) or a general minimal PyTorch/NVBit incompatibility (C), because
the C2--C4 first kernels all completed. It also does not establish a need to
run longer: a future, separately authorized long diagnostic could be useful
only if it retains an exact and bounded function/related-function scope. This
publication grants no such authorization and does not reopen the closed
one-shot long-watch, model, trace, or C-target paths.
