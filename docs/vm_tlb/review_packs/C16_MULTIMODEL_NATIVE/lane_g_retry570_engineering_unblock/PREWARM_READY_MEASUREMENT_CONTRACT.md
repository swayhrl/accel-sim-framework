# Retry570 prewarm/READY/measurement contract

This is an engineering qualification, not permission to run a model, trace,
scientific capture, or C target.

The only currently qualified unblock candidate is the frozen NVBit 1.7.5
archive/core combined with the existing Lane G tracer source. A future,
separately authorized process must follow this order:

1. verify GPU, driver 570.124.04, CUDA 12.4, torch 2.5.1+cu124,
   `libtorch_cuda.so`, NVBit archive/core, and Lane G tool hashes;
2. set `CUDA_MODULE_LOADING=EAGER` before process start;
3. outside `MEASUREMENT_ACTIVE`, execute a bounded no-trace prewarm;
4. require normal exit, first-kernel completion, zero `.trace` payloads, and
   no surviving child before emitting `READY`;
5. only after `READY`, acquire the shared budget lease and create
   `MEASUREMENT_ACTIVE` for a separately authorized formal capture.

Prewarm artifacts and timing are diagnostic-only and must never enter native
timing or C/H scientific inputs. A version switch is an implementation change,
so any future model/capture requires a clean source/tool checkpoint plus model-
level identity/correctness requalification. NVBit 1.8 remains unqualified on
this node; no timeout extension is implied.
