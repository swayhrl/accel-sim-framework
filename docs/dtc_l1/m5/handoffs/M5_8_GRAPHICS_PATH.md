# M5.8 Source-Backed Graphics Path Recovery

Terminal status: **`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`**
Scope: the authorized graphics-research branch only.  No Core file, compute worktree,
job, output directory, formal Base/IO/OO run, or M5.9 implementation was changed.

## Result

M5.7 provides source-equivalent scene evidence for four labels and preserves the
unresolved `2D-tex` gap.  It does **not** supply the missing operational bridge from an
OpenGL ES/2 graphics draw to this Framework's DTC-L1 timing model.  The ordered routes
below were therefore audited rather than treating the prior current-infrastructure
failure as dispositive.

No route reaches the required minimum: source-identified shader stages, graphics
thread/warp grouping, dynamic addresses/request sizes, global-vs-texture semantics,
ordering/completion, draw/frame boundaries, framebuffer/fixed-function scope, and a
cycle definition which causes Base/IO/OO to exercise the *same* DTC mechanism.  A
memory proxy is consequently not formal graphics reproduction and is not proposed.

## Ordered recovery audit

| Order / candidate | Sources examined | Evidence and disposition |
| --- | --- | --- |
| 1. Original thesis/project simulator, artifacts, traces, scripts | local Framework source/docs and handoffs; all locally discoverable graphics-named source artifacts | Only the Table-4.1 transcription and pre-existing G0/G1 handoffs exist.  No [78] metadata, project tree, run script, request trace, shader binary, draw/frame log, or 128x128 2D asset is present. **Ruled out for this evidence set.** |
| 2. Author/group historical repository and release lineage | official [glmark2 history](https://github.com/glmark2/glmark2), 2014 anchor and 2020.04--2023.01 tags | Sources and stable assets recover scene identity, not a simulator, trace, original paper command, or graphics request semantics. **Provenance succeeds; execution/replay route absent.** |
| 3. Historical graphics-enabled GPGPU-Sim/Accel-Sim artifacts | current Core history (`OPENGL_SUPPORT` introduced historically); upstream [GPGPU-Sim](https://github.com/gpgpu-sim/gpgpu-sim_distribution); remote-branch inventory; public historical graphics-trace result | The surviving support is CUDA--OpenGL buffer interop (`cudaGLMapBufferObject`/unmap), not an OpenGL renderer, shader compiler, vertex/fragment scheduler, or glmark2 trace reader.  No graphics branch/artifact for these five scenes is present in the named remotes.  The externally discoverable `gem5-graphics`/Emerald route documents a **textured-cube** trace and is a different simulator, not a glmark2 five-scene artifact nor this DTC mechanism. **Ruled out.** |
| 4. Defensible direct graphics frontend integration | static audit of `libcuda/cuda_runtime_api.cc`, build default, and Framework/Core interfaces | `OPENGL_SUPPORT` is disabled by default.  Even if enabled, it copies a CUDA-mapped GL buffer to/from simulated memory; it neither executes GL shaders nor owns draw/frame/fixed-function state.  A new frontend would require a new graphics ISA/IR bridge and semantics not supplied by source artifacts.  It cannot be called a recovered direct path and is outside M5.8/M5.9 authorization. **Not established.** |
| 5. Source-backed shader/request capture/replay | current Core README, trace interfaces and source search; source artifact inventory | Framework trace mode accepts NVBit-generated NVIDIA **CUDA SASS** traces.  Simulator `shader_trace` is diagnostic naming for CUDA SIMT shader cores, not a graphics shader trace.  There is no glmark2 capture/replay format or capture artifact, and no replay contract retaining shader stage, texture space, draw/frame, framebuffer, or completion semantics. **Ruled out.** |
| 6. Proxy | existing guidance only | A calibrated memory proxy could later be supplemental only after a formal route exists; it cannot establish the missing scene identity/semantics or produce paper graphics results. **Excluded from formal reproduction.** |

The negative conclusion is bounded to the explicitly named original-artifact,
historical-simulator, direct, and trace/replay sources available to this track and
their official/upstream histories.  It does not assert that an unknown private archive
can never surface; such an archive would reopen M5.8 under the admission contract
below rather than make a proxy valid.

## DIRECT/TRACE semantic admission table

| Candidate | shader-stage identity | thread / warp / grouping | addresses + request sizes | global vs texture semantics | ordering + completion | draw / frame boundary | framebuffer / fixed function | cycle / performance metric | same Base/IO/OO mechanism? | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Core CUDA--GL interop direct candidate | no GL vertex/fragment shader; only CUDA kernel path | CUDA CTA/warp only; no graphics primitive/raster groups | one mapped GL buffer copied to CUDA allocation; no dynamic graphics requests | no sampler/texture fetch identity | CUDA API return only; no graphics completion/fence contract | none | absent | CUDA-kernel simulation cycles, not frame time | no | reject |
| Core/Accel-Sim NVBit SASS replay candidate | CUDA SASS kernel only | CTA/warp from CUDA trace only | trace can encode CUDA memory ops, but no five-scene trace exists | no GL texture target/sampler semantics | CUDA kernel completion only | none | absent | trace-kernel cycles; no per-frame definition | no | reject |
| historical graphics trace candidate (Emerald/gem5 discovery) | not supplied for these scenes | not mapped to this Core | no five-scene trace/artifact | unverified for this workload set | not available | only an unrelated textured-cube trace is described | outside Framework/Core | incomparable simulator metric | no | reject |
| hypothetical new direct frontend | unknown until a new compiler/IR/capture source exists | must define primitive-to-workgroup mapping | must capture dynamic requests and sizes | must preserve GL target/sampler space | must define visibility/fence/readback | must emit draw/frame IDs | must model or bound fixed function/framebuffer | must define GPU cycles and frame aggregation | cannot demonstrate yet | not a recovered path; no M5.9 plan |

## Reopening condition (not an implementation plan)

Only a newly recovered original artifact may reopen this result.  Before any M5.9
authorization it must provide, for at least jellyfish, one textured scene, and horse:

1. immutable source/asset/trace hashes and the exact glmark2 command;
2. per-stage shader identity and primitive/raster/thread-to-warp mapping;
3. dynamic address, size, memory-space, texture-target, ordering, completion, draw,
   frame, and framebuffer/fixed-function records;
4. a validated replay-to-Core mapping plus a frame-completion and cycle metric; and
5. a proof that Base/IO/OO change only the validated DTC-L1 mechanism while replaying
   identical graphics input.

Without all five, the artifact is diagnostic/proxy material only and cannot change the
terminal status.
