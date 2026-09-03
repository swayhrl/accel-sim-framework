# M5 Graphics Path Audit

Status: `UNAVAILABLE_WITH_CURRENT_INFRA` for direct/replayed thesis graphics.

## Evidence

1. The recovered glmark2 source is an OpenGL 2.0 / ES 2.0 scene benchmark;
   its scenes execute OpenGL model, shader, texture, draw, and framebuffer
   operations.
2. The active Core source has no production glmark2/OpenGL scene frontend or
   shader-stage capture/replay path.  Its trace controls are simulator-internal
   CUDA warp/scheduler/scoreboard diagnostics, not a source-backed graphics
   request stream.
3. `libcuda/cuda_runtime_api.cc` makes its CUDA--OpenGL buffer map/unmap
   implementation conditional on `OPENGL_SUPPORT`; the active disabled branch
   prints `GPGPU-Sim support for OpenGL integration disabled -- exiting` and
   terminates.  This cannot execute glmark2's graphics pipeline.
4. The top-level CMake OpenGL dependency is not an end-to-end graphics
   frontend and does not supply fixed-function, vertex/fragment, texture,
   framebuffer, or source-domain completion semantics.

Consequently neither `DIRECT_SOURCE_BACKED` nor `TRACE_SOURCE_BACKED` is
established. A memory proxy would discard shader/order/completion semantics and
is not authorized as a replacement for the paper graphics bars.  No graphics
result, figure extension, or `GM-ALL-PAPER` aggregate may be emitted from this
infrastructure.
