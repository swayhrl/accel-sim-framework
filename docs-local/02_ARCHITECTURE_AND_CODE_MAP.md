# Accel-Sim / GPGPU-Sim Architecture and Code Map

This document is a source-oriented map of the simulator itself. It is intended for developers who need to understand, debug, or modify Accel-Sim and the embedded GPGPU-Sim timing model without first reverse-engineering the repository structure.

The descriptions below are based on the following source anchors:

- Accel-Sim Framework: `d930ad6d02c09bb56867132583735aba0389cff4`
- GPGPU-Sim: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`

The main principle to keep in mind is that **Accel-Sim and GPGPU-Sim are two distinct repositories with different responsibilities**. Accel-Sim adds the SASS trace frontend, trace parsing, trace-to-timing-instruction conversion, tested configurations, and experiment orchestration. GPGPU-Sim provides the execution-driven PTX path and the common cycle-level GPU timing model used by both PTX and SASS modes.

---

## 1. High-level mental model

```text
Accel-Sim Framework
|
|-- SASS trace input and parser
|-- SASS ISA -> timing-instruction translation
|-- trace-specific configuration
|-- job launching / monitoring / statistics workflow
|
`-- gpu-simulator/gpgpu-sim/             (independent Git repository)
    |
    |-- PTX functional execution
    |-- kernel / stream runtime model
    |-- SM timing model
    |-- warp scheduling / scoreboard / operand collectors
    |-- execution units
    |-- load-store pipeline
    |-- L1 / L2 caches
    |-- interconnect
    |-- memory partitions / DRAM
    `-- common cycle-level simulation engine
```

The two principal execution paths are therefore:

```text
SASS trace-driven:
trace files
  -> Accel-Sim trace parser
  -> trace_warp_inst_t / trace_kernel_info_t
  -> GPGPU-Sim timing model

PTX execution-driven:
CUDA application / PTX
  -> GPGPU-Sim CUDA runtime interception
  -> cuda-sim functional execution
  -> dynamic warp instructions
  -> GPGPU-Sim timing model
```

Once an instruction enters the timing model, most of the shader, cache, interconnect, and DRAM machinery is shared.

---

## 2. Repository boundary and top-level code map

### Accel-Sim Framework repository

Important paths:

```text
gpu-simulator/
|-- accel-sim.cc                 SASS trace-driven top-level simulation loop
|-- accel-sim.h
|-- trace-parser/                Trace-file grammar and decoding
|-- trace-driven/                SASS trace -> timing-model bridge
|-- ISA_Def/                     Per-architecture SASS opcode maps
|-- configs/tested-cfgs/         Trace-side tested configurations
`-- gpgpu-sim/                   Independent GPGPU-Sim Git repository

util/
`-- job_launching/               Run-directory creation, launcher, monitor, stats
```

### GPGPU-Sim repository

Important paths:

```text
src/
|-- abstract_hardware_model.*    warp_inst_t, mem_access_t, coalescing
|-- gpgpusim_entrypoint.*        PTX simulator/runtime entry and simulation thread
|-- cuda-sim/                    PTX parsing and functional execution
|-- libcuda/                     CUDA runtime / driver emulation and context support
`-- gpgpu-sim/
    |-- gpu-sim.*                top-level timing model and clock-domain advancement
    |-- shader.*                 SM, warp scheduler, pipelines, LD/ST unit
    |-- scoreboard.*             register dependency tracking
    |-- stack.*                  SIMT stack / control-flow state
    |-- gpu-cache.*              generic cache, tag array, MSHR, L1 cache machinery
    |-- mem_fetch.*              memory-request object
    |-- icnt_wrapper.*           interconnect abstraction boundary
    |-- local_interconnect.*     built-in local crossbar
    |-- l2cache.*                L2 + memory-subpartition / partition plumbing
    |-- dram.*                   DRAM timing model
    |-- dram_sched.*             DRAM scheduling
    |-- addrdec.*                memory address decoding / partition mapping
    `-- stats / power / trace support files
```

---

## 3. SASS trace-driven execution path

### 3.1 Top-level flow

The trace-driven executable enters through `gpu-simulator/accel-sim.cc`.

Conceptually:

```text
kernelslist.g
   |
   v
trace_parser::parse_commandlist_file()
   |
   +-- MemcpyHtoD command
   |      -> perf_memcpy_to_gpu()
   |
   `-- kernel command
          -> trace_parser::parse_kernel_info()
          -> create_kernel_info()
          -> trace_kernel_info_t
          -> gpgpu_sim::launch()
          -> cycle-level simulation
```

`accel_sim_framework::simulation_loop()` repeatedly:

1. fills a window of pending commands;
2. constructs `trace_kernel_info_t` objects;
3. launches kernels when the simulated GPU and CUDA stream are available;
4. calls the common timing model through `m_gpgpu_sim->cycle()`;
5. detects completed kernels;
6. finalizes trace state and prints statistics.

The SASS path therefore does **not** bypass GPGPU-Sim timing. It replaces PTX functional instruction generation with recorded instruction traces, then feeds those instructions into a trace-specific shader implementation derived from the same timing model.

### 3.2 Trace parser

Primary files:

```text
gpu-simulator/trace-parser/trace_parser.h
gpu-simulator/trace-parser/trace_parser.cc
gpu-simulator/trace-parser/warp_trace_stream.h
```

Important types:

- `trace_parser`
- `trace_command`
- `kernel_trace_t`
- `inst_trace_t`
- `PipeReader`
- `WarpTraceStream`

`trace_parser` parses the command list and kernel metadata. `inst_trace_t` represents one traced warp instruction and carries information such as:

- CTA / cluster identity;
- PC;
- active-lane mask;
- source and destination registers;
- opcode string;
- memory-width and memory-address information;
- immediates;
- optional register values;
- TMA-specific metadata for newer trace formats.

The trace parser supports multiple address encodings, including full address lists, base+stride, base+delta, and TMA-specific forms. Memory-address payloads are owned through `std::unique_ptr`, so parser/trace objects have explicit move-only ownership semantics.

### 3.3 Trace-to-timing bridge

Primary files:

```text
gpu-simulator/trace-driven/trace_driven.h
gpu-simulator/trace-driven/trace_driven.cc
```

The most important classes are:

- `trace_gpgpu_sim : public gpgpu_sim`
- `trace_simt_core_cluster : public simt_core_cluster`
- `trace_shader_core_ctx : public shader_core_ctx`
- `trace_kernel_info_t : public kernel_info_t`
- `trace_shd_warp_t : public shd_warp_t`
- `trace_warp_inst_t : public warp_inst_t`

The key instruction-conversion path is:

```text
trace_shd_warp_t::get_next_trace_inst()
       |
       v
trace_warp_inst_t::parse_from_trace_struct()
       |
       v
warp_inst_t-compatible timing instruction
```

`trace_kernel_info_t` selects an architecture-specific opcode map according to the trace binary version (for example Volta, Ampere, Hopper). `trace_warp_inst_t::parse_from_trace_struct()` then transfers the traced PC, active mask, register operands, addresses, operation type, and latency information into the timing instruction used by the shader model.

### 3.4 NVBit is not part of replay runtime

`util/tracer_nvbit/` is the producer used when collecting new SASS traces on a real GPU. It is **not** on the execution path when replaying an already-existing trace. Existing SASS traces require the parser, trace-driven frontend, configuration, and timing model, but not a running NVBit tracer.

---

## 4. PTX execution-driven path

The PTX path is primarily inside the nested GPGPU-Sim repository.

Important files/directories:

```text
gpu-simulator/gpgpu-sim/src/gpgpusim_entrypoint.*
gpu-simulator/gpgpu-sim/src/cuda-sim/
gpu-simulator/gpgpu-sim/libcuda/
```

`gpgpu_context::gpgpu_ptx_sim_init_perf()` creates the execution-driven timing model (`exec_gpgpu_sim`) and its stream manager.

The simulation thread then alternates between runtime operations, functional execution, and timing execution:

```text
CUDA runtime operation / kernel launch
          |
          v
stream_manager
          |
          v
cuda-sim functional execution
(gpgpu_cuda_ptx_sim_main_func)
          |
          v
dynamic instructions / memory behavior
          |
          v
gpgpu_sim::cycle()
```

The functional simulator executes PTX semantics and generates the dynamic behavior needed by the timing model. The timing model then accounts for scheduler, pipeline, cache, interconnect, and DRAM timing.

This is the main architectural difference between the two modes:

```text
PTX mode:  functional execution generates instructions dynamically
SASS mode: recorded trace supplies instructions directly
```

The downstream timing model is largely shared.

---

## 5. Global timing model and GPU hierarchy

The top-level timing model is centered around `gpgpu_sim` in:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc
```

At a high level:

```text
gpgpu_sim
|
|-- SIMT core clusters
|     `-- shader cores (SM model)
|
|-- interconnect
|
|-- memory subpartitions
|     `-- L2 cache
|
`-- memory partitions
      `-- DRAM controller / DRAM model
```

`gpgpu_sim::cycle()` advances multiple modeled clock domains. The major domains are:

- CORE
- ICNT
- L2
- DRAM

The simulator advances whichever domains are due on a given global step. This is important when debugging latency because a request may wait not only on queue occupancy, but also on the next eligible clock-domain event.

`gpgpu_sim::active()` considers outstanding work in shader cores, memory partitions, interconnect, and pending CTAs when deciding whether the simulated device is still active.

---

## 6. SIMT core cluster and SM organization

The simulated SM is called a **shader core** in GPGPU-Sim source code.

Primary files:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.cc
```

Two important hierarchy classes are:

```text
simt_core_cluster
  `-- one or more shader_core_ctx objects
```

`simt_core_cluster` groups shader cores and provides the boundary between shader-side traffic and the interconnect. `shader_core_ctx` models a single SM-like core.

The shader-core state includes, among other things:

- resident CTA / hardware-thread allocation state;
- warp state (`shd_warp_t`);
- barriers;
- instruction-fetch buffer;
- per-warp SIMT stack;
- warp schedulers;
- register dependency scoreboard;
- operand collectors / register-bank model;
- pipeline register sets;
- execution units;
- result buses;
- load-store unit;
- L1 instruction, constant, texture, and data caches;
- shared-memory timing and bank model;
- statistics and occupancy/resource state.

### 6.1 Shader-core cycle

The shader core is explicitly cycle-stepped. The main per-cycle path includes the familiar pipeline phases:

```text
writeback
   ^
   |
execute
   ^
   |
read operands / operand collection
   ^
   |
issue
   ^
   |
decode
   ^
   |
fetch
```

The exact implementation is distributed across methods in `shader.cc`, but `shader_core_ctx::cycle()` is the central per-SM timing entry point.

### 6.2 Warp representation

`shd_warp_t` stores timing state for a warp, including:

- active/completed lanes;
- warp and dynamic-warp IDs;
- instruction buffer;
- outstanding stores and atomics;
- memory-barrier state;
- stream ID;
- synchronization state;
- TMA / GMMA related tracking on newer modeled ISAs;
- replay-related state in the trace-driven subclass.

For trace-driven simulation, `trace_shd_warp_t` extends this behavior with a trace PC and a trace-instruction stream.

### 6.3 SIMT control flow

SIMT control-flow state is represented through the SIMT stack implementation in:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/stack.*
```

Schedulers receive SIMT-stack state when choosing and issuing warp instructions. Trace-driven shader cores override selected control-flow behavior where needed to reconstruct behavior from trace information.

### 6.4 Warp schedulers

Scheduler classes are declared in `shader.h` and implemented in `shader.cc`. The model supports multiple scheduling policies, including variants such as:

- Loose Round Robin (LRR)
- Greedy-Then-Oldest (GTO)
- Two-Level Active
- Warp Limiting
- Oldest-First
- other configured policies present in the source

A scheduler owns/supervises a subset of warps, checks whether candidate warps are ready, consults scoreboard/SIMT state, and issues ready instructions into the appropriate pipeline register.

For scheduler-related work, start from:

```text
scheduler_unit
shader_core_ctx::create_schedulers()
shader_core_ctx::issue_warp()
```

### 6.5 Scoreboard and register dependencies

Primary files:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/scoreboard.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/scoreboard.cc
```

`Scoreboard` tracks pending register writes per warp. Important operations include:

- `reserveRegisters()`
- `releaseRegisters()`
- `checkCollision()`
- `pendingWrites()`

A scheduler uses scoreboard state to prevent issue when source/destination dependencies are unresolved. Long-latency dependencies, such as memory operations, are tracked separately as long-operation registers.

### 6.6 Pipeline registers

Pipeline register sets are represented by `register_set` objects. The standard stage names include:

```text
ID_OC_SP
ID_OC_DP
ID_OC_INT
ID_OC_SFU
ID_OC_MEM
OC_EX_SP
OC_EX_DP
OC_EX_INT
OC_EX_SFU
OC_EX_MEM
EX_WB
ID_OC_TENSOR_CORE
OC_EX_TENSOR_CORE
```

Additional specialized-unit pipeline registers can be created from configuration.

The configured width of these stages is controlled by shader-core configuration (`pipe_widths` / pipeline-width configuration).

### 6.7 Operand collectors and register-file bank model

Operand collection is also implemented in `shader.*`.

Important classes/functions include:

- `opndcoll_base_t`
- `opndcoll_rfu_t`
- `register_bank()`
- collector-unit and arbiter structures in `shader.h`

The operand collector models register-file access and bank conflicts before an instruction reaches an execution unit. When the sub-core model is enabled, issue partitions and register-bank resources can be partitioned by scheduler.

### 6.8 Execution units

The shader-core execution-unit vector is held in `shader_core_ctx::m_fu`. Units are instantiated in `create_exec_pipeline()` according to the configuration.

Common execution-unit classes include:

```text
SP / FP pipeline
DP pipeline
INT pipeline
SFU
tensor-core pipeline
specialized units
LD/ST unit
```

The standard units feed the writeback/result-bus path, while the LD/ST unit is stallable and interacts with the memory hierarchy.

The source creates configured counts of SP, DP, INT, SFU, tensor, and specialized units and associates each with dispatch/issue pipeline ports.

### 6.9 Configurable shared-core vs sub-core model

GPGPU-Sim 4.x supports both shared and partitioned/sub-core organizations.

With `-gpgpu_sub_core_model 1`, scheduler-visible resources can be partitioned so that each scheduler is associated with its own issue partition, register-file resources, operand collectors, and execution-unit subset while still sharing other SM-level resources such as memory structures according to the configuration.

This is the main abstraction used to model Volta-style sub-core organization.

---

## 7. Instruction fetch, instruction cache, and front end

Instruction-cache state is created inside the shader core. The shader model includes a dedicated L1 instruction cache (`m_L1I`) and an instruction fetch buffer.

Front-end debugging normally starts from:

```text
shader_core_ctx::fetch()
shader_core_ctx::decode()
ifetch_buffer_t
m_L1I
```

The front end selects a warp PC, accesses the instruction cache, receives instruction data, fills the instruction buffer, decodes instructions, and makes them visible to warp schedulers.

In trace-driven mode the front end ultimately obtains the next timing instruction through `trace_shd_warp_t::get_next_trace_inst()` instead of decoding PTX into a dynamic instruction in the same way as the execution-driven frontend.

---

## 8. Shared memory and on-SM memory structures

The SM model includes several distinct on-chip memory structures:

```text
L1I   instruction cache
L1C   constant / read-only cache
L1T   texture cache
L1D   data cache
shared memory / scratchpad
```

The data-cache and LD/ST path are discussed below. Shared-memory bank timing and shared-memory latency are modeled within the shader/LDST machinery and configured by shader-core options.

The cache and shared-memory capacities can also participate in architecture-specific unified/adaptive configurations, as documented in `gpu-simulator/gpgpu-sim4.md` and the tested architecture configuration files.

---

## 9. Dynamic memory accesses and coalescing

Before requests enter the cache hierarchy, warp-level memory operations are converted into memory transactions.

Primary files:

```text
gpu-simulator/gpgpu-sim/src/abstract_hardware_model.h
gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc
```

Important types/functions:

- `warp_inst_t`
- `mem_access_t`
- `warp_inst_t::generate_mem_accesses()`
- memory-coalescing helpers in `warp_inst_t`

Conceptually:

```text
per-lane addresses in warp_inst_t
          |
          v
memory coalescing
          |
          v
one or more mem_access_t transactions
          |
          v
LD/ST unit
```

`generate_mem_accesses()` classifies accesses by memory space and read/write type, models shared-memory bank accesses when appropriate, and builds the transaction queue consumed by the LD/ST unit.

When debugging transaction counts, sector masks, byte masks, or coalescing behavior, this is the first layer to inspect.

---

## 10. Load-store unit and L1 path

The load-store pipeline is implemented primarily in `shader.*` through `ldst_unit`.

Important functions include:

```text
ldst_unit::cycle()
ldst_unit::process_memory_access_queue_l1cache()
ldst_unit::process_cache_access()
ldst_unit::L1_latency_queue_cycle()
```

The rough path for a global/local memory operation is:

```text
warp_inst_t access queue
      |
      v
ldst_unit
      |
      +-- L1D access
      |      |
      |      +-- hit -> completion path
      |      `-- miss -> mem_fetch -> interconnect
      |
      `-- L1 bypass -> mem_fetch -> interconnect
```

`m_L1D->access()` is the key L1D cache access call. If configuration or instruction cache policy bypasses L1, the LD/ST unit allocates a `mem_fetch` and pushes it directly through the shader-side memory interface.

---

## 11. Memory request object: `mem_fetch`

Primary files:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/mem_fetch.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/mem_fetch.cc
```

`mem_fetch` is the principal request object that moves through the memory hierarchy after a memory transaction leaves the shader pipeline.

It records information including:

- request UID;
- shader / TPC / warp identity;
- request/reply type;
- underlying `mem_access_t`;
- address and request size;
- byte and sector masks;
- target memory subpartition;
- request status;
- timestamps;
- stream ID;
- links to original requests when a request is split or transformed.

When tracing a lost request, unexpected latency, wrong partition mapping, or stalled response, follow the same `mem_fetch` through its status transitions.

---

## 12. Generic cache model

Primary files:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-cache.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-cache.cc
```

This layer implements most reusable cache behavior, including:

- cache-line / sector state;
- tag arrays;
- replacement/indexing behavior;
- reservation state;
- MSHRs and MSHR merging;
- miss queues;
- fill paths;
- write policy / allocation policy;
- data-cache base behavior;
- L1 cache behavior;
- statistics.

The class hierarchy includes generic cache structures such as `baseline_cache` and `data_cache`; `l1_cache` derives from the data-cache machinery.

This distinction is useful:

```text
gpu-cache.*
  = reusable cache-internal mechanisms

l2cache.*
  = L2 placement inside the memory-subpartition / DRAM plumbing
```

---

## 13. Interconnect abstraction

The stable simulator boundary for the on-chip network is:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/icnt_wrapper.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/icnt_wrapper.cc
```

The wrapper exports operations such as:

- `icnt_create`
- `icnt_init`
- `icnt_has_buffer`
- `icnt_push`
- `icnt_pop`
- `icnt_transfer`
- `icnt_busy`

The implementation is selectable. The current source supports at least:

```text
INTERSIM
LOCAL_XBAR
```

Therefore `src/intersim2/` should not be treated as the only possible request path. Code that wants to remain network-implementation agnostic should use the interconnect wrapper boundary.

---

## 14. L2 cache and memory-subpartition organization

Primary files:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/l2cache.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/l2cache.cc
```

Important classes:

- `l2_cache`
- `memory_sub_partition`
- `memory_partition_unit`
- `partition_mf_allocator`

The memory subsystem is organized roughly as:

```text
interconnect
     |
     v
memory_sub_partition
     |
     +-- icnt -> L2 queue
     |
     +-- L2 cache
     |
     +-- L2 -> DRAM queue
     |
     +-- DRAM -> L2 queue
     |
     `-- L2 -> icnt queue
            |
            v
       interconnect response
```

The source explicitly instantiates the four main queue directions:

```text
icnt-to-L2
L2-to-dram
dram-to-L2
L2-to-icnt
```

`memory_sub_partition::cache_cycle()` services L2 responses, requests entering from the interconnect, L2 accesses, fills, and queue movement.

`memory_partition_unit` groups one or more subpartitions with the DRAM controller side and arbitrates requests into DRAM.

---

## 15. DRAM model

Primary files:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/dram.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/dram.cc
gpu-simulator/gpgpu-sim/src/gpgpu-sim/dram_sched.h
gpu-simulator/gpgpu-sim/src/gpgpu-sim/dram_sched.cc
```

`memory_partition_unit::dram_cycle()` is the important bridge between the L2-side queues and the detailed DRAM model.

The DRAM model accounts for controller queues, bank/bank-group timing, scheduling, command timing, data return, and statistics according to the architecture configuration.

Address-to-controller/bank mapping is handled separately by:

```text
gpu-simulator/gpgpu-sim/src/gpgpu-sim/addrdec.*
```

---

## 16. End-to-end memory request path

A useful source-level request lifecycle is:

```text
warp instruction
    |
    v
warp_inst_t::generate_mem_accesses()
    |
    v
mem_access_t transaction(s)
    |
    v
ldst_unit
    |
    +---------------- L1 hit ---------------------------+
    |                                                   |
    `-- L1 miss / bypass                                |
             |                                          |
             v                                          |
          mem_fetch                                     |
             |                                          |
             v                                          |
      shader memory interface                           |
             |                                          |
             v                                          |
        icnt_wrapper                                    |
             |                                          |
             v                                          |
     memory_sub_partition                               |
             |                                          |
             v                                          |
            L2                                          |
             |                                          |
             v                                          |
       L2 -> DRAM queue                                 |
             |                                          |
             v                                          |
   memory_partition_unit                                |
             |                                          |
             v                                          |
           DRAM                                         |
             |                                          |
             v                                          |
       DRAM -> L2                                       |
             |                                          |
             v                                          |
       L2 -> ICNT                                       |
             |                                          |
             v                                          |
        icnt_wrapper                                    |
             |                                          |
             v                                          |
 simt_core_cluster::icnt_cycle()                        |
             |                                          |
             v                                          |
          ldst_unit                                     |
             |                                          |
             +------------- writeback / completion -----+
```

This path is the best starting point for debugging memory latency and request lifetime.

---

## 17. Response path back to the SM

A memory response leaves the memory-subpartition through the L2-to-interconnect queue. `gpgpu_sim` pushes the response into the interconnect when the destination has space.

At the shader side:

```text
simt_core_cluster::icnt_cycle()
```

accepts responses from the network and routes them to instruction-cache or LD/ST response handling depending on access type. The LD/ST unit then completes loads, store acknowledgements, atomics, cache fills, and register writeback as appropriate.

---

## 18. Configuration layering

The simulator has several configuration layers with different responsibilities.

### 18.1 GPGPU-Sim architecture configuration

Typical location:

```text
gpu-simulator/gpgpu-sim/configs/tested-cfgs/<GPU>/gpgpusim.config
```

This controls the microarchitecture and memory system, for example:

- number of clusters / shader cores;
- warp schedulers;
- sub-core mode;
- execution-unit counts;
- pipeline widths;
- register-file and operand-collector resources;
- shared-memory properties;
- L1 and L2 cache parameters;
- memory partitions;
- interconnect mode;
- DRAM timing;
- clock frequencies;
- runtime/deadlock/statistics options.

### 18.2 Trace-side configuration

For SASS trace-driven mode, Accel-Sim also uses a trace configuration such as:

```text
gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
```

This contains trace-specific instruction-latency and specialized-unit mappings, such as latency/initiation parameters for integer, SP, DP, SFU, tensor, and configured specialized execution units.

In short:

```text
gpgpusim.config
  -> GPU resource/timing/memory architecture

trace.config
  -> trace/SASS instruction timing and specialized-unit mapping
```

Do not treat the two files as interchangeable.

---

## 19. Specialized execution units and ISA maps

Trace-driven mode separates machine-opcode recognition from the generic shader timing model.

Important paths:

```text
gpu-simulator/ISA_Def/
gpu-simulator/trace-driven/
```

Architecture-specific opcode maps classify SASS instructions into timing-model operation categories. `trace_warp_inst_t::parse_from_trace_struct()` uses those maps, while `trace_config` supplies latency/initiation information.

This mechanism allows trace-driven simulation to represent architecture-specific operation classes without duplicating the entire shader pipeline.

---

## 20. Job launching, monitoring, and statistics

Experiment orchestration is separate from the GPU microarchitecture model.

Primary path:

```text
util/job_launching/
```

Important scripts include:

- `run_simulations.py`
- `monitor_func_test.py`
- `get_stats.py`
- shared helper modules and launch templates

`run_simulations.py` is responsible for experiment setup rather than GPU timing. It:

1. resolves benchmark and configuration descriptions;
2. creates run directories;
3. links/copies data, trace, and configuration files;
4. generates the simulation launch template;
5. submits the job through the selected launcher (`local`, Slurm, etc.);
6. records launch metadata.

A useful debugging rule is:

```text
job did not start / run directory wrong / data missing
    -> inspect util/job_launching first

simulation starts but timing, IPC, cache, or memory behavior is wrong
    -> inspect simulator core
```

---

## 21. Statistics, power, and observability

Statistics are distributed across shader, cache, memory, and global simulator objects.

Common places to inspect include:

```text
shader.*              shader/warp/pipeline/cache statistics
gpu-cache.*           cache access/miss/MSHR statistics
l2cache.*             L2/memory-subpartition statistics
dram.*                DRAM timing/bank statistics
mem_latency_stat.*    request-latency statistics
gpu-sim.*             global and per-kernel statistics
stats.*                shader/core statistics support
power_* / accelwattch power-model integration
```

When adding new statistics, place them close to the component that owns the modeled event rather than inferring them later from logs whenever possible.

---

## 22. Practical modification map

| Goal | First files/classes to inspect |
|---|---|
| Understand SASS trace grammar | `trace-parser/trace_parser.*` |
| Add/inspect SASS opcode mapping | `ISA_Def/*`, `trace-driven/trace_driven.*` |
| Change trace-driven kernel/warp behavior | `trace-driven/trace_driven.*`, `accel-sim.cc` |
| Change PTX functional semantics | `gpgpu-sim/src/cuda-sim/*` |
| Change CUDA runtime / stream behavior | `gpgpusim_entrypoint.*`, `libcuda/*`, `stream_manager.*` |
| Change CTA / warp state | `shader.*`, `abstract_hardware_model.*` |
| Change warp scheduler | scheduler classes in `shader.*` |
| Change dependency handling | `scoreboard.*` |
| Change SIMT divergence/control flow | `stack.*`, shader issue/control-flow code |
| Change register-file / operand collector | operand-collector and register-bank code in `shader.*` |
| Change SP/INT/DP/SFU/tensor execution | execution-unit classes and `create_exec_pipeline()` in `shader.*` |
| Change pipeline widths/ports | `shader_core_config`, pipeline registers in `shader.*`, config |
| Change instruction cache/front end | fetch/decode code in `shader.*`, L1I config |
| Change shared-memory timing/banks | LD/ST/shared-memory code in `shader.*`, config |
| Change memory coalescing | `abstract_hardware_model.*` |
| Change L1D behavior | `shader.*` (`ldst_unit`) and `gpu-cache.*` |
| Change cache tags/MSHR/replacement | `gpu-cache.*` |
| Trace a memory request | `mem_fetch.*` and `mem_fetch_status` transitions |
| Change interconnect-independent interface | `icnt_wrapper.*` |
| Change built-in local crossbar | `local_interconnect.*` |
| Change L2 internal cache policy | `gpu-cache.*`, `l2cache.*` |
| Change L2 queueing / memory subpartition | `l2cache.*` |
| Change address partition mapping | `addrdec.*` |
| Change DRAM scheduling/timing | `dram.*`, `dram_sched.*` |
| Change global timing-domain behavior | `gpu-sim.*` |
| Change experiment launch workflow | `util/job_launching/*` |
| Change statistics extraction workflow | `util/job_launching/get_stats.py` and component statistics |

---

## 23. Recommended debugging order

### A simulation does not launch

Check in this order:

```text
benchmark/config definition
-> run_simulations.py
-> generated run directory
-> generated launch script
-> executable / shared-library environment
```

### Trace-driven simulation fails while parsing

```text
kernelslist.g
-> trace_parser::parse_commandlist_file()
-> kernel_trace_t / trace header
-> inst_trace_t::parse_from_string()
-> opcode map
-> trace_warp_inst_t::parse_from_trace_struct()
```

### A warp is not issuing

```text
warp active/waiting state
-> SIMT stack
-> scoreboard collision
-> scheduler policy
-> pipeline-register availability
-> operand collector / register-bank conflict
-> execution-unit availability
```

### A memory instruction stalls

```text
warp_inst_t access queue
-> coalescing / mem_access_t generation
-> ldst_unit
-> L1 access or bypass
-> mem_fetch status
-> interconnect buffer
-> memory_sub_partition queues
-> L2 access/MSHR
-> DRAM queue/scheduler
-> response path
```

### A kernel never completes

Check both compute and memory-side liveness:

```text
outstanding warps / CTA state
pending scoreboard writes
outstanding stores / atomics
LD/ST response queues
interconnect busy state
memory-subpartition busy state
DRAM return queues
stream-manager state
```

`gpgpu_sim::active()` and the simulator's deadlock diagnostics are useful global checkpoints because they aggregate activity from shader, memory, interconnect, and pending kernel work.

---

## 24. Source-level invariants worth preserving

When modifying the simulator, several boundaries are especially important:

1. **Framework and nested GPGPU-Sim are separate repositories.** Keep their histories and source identities explicit.
2. **Trace replay and PTX execution differ mainly at instruction-generation time.** Avoid duplicating downstream timing behavior unnecessarily.
3. **`warp_inst_t` / `mem_access_t` / `mem_fetch` are different abstraction levels.** A warp instruction can generate multiple memory transactions, and each transaction can become one or more memory requests depending on cache/sector behavior.
4. **The LD/ST unit owns the shader-side transition into the memory hierarchy.**
5. **`gpu-cache.*` is the reusable cache mechanism layer; `l2cache.*` places L2 inside the memory-partition system.**
6. **Use `icnt_wrapper.*` as the interconnect abstraction boundary.** Do not assume one concrete network implementation.
7. **Clock domains matter.** A component can be logically ready but still wait for its modeled domain to advance.
8. **Configuration is part of the model.** When debugging a behavioral difference, record both source identity and the exact `gpgpusim.config` / `trace.config` used.

---

## 25. Minimal reading sequence for a new developer

For a fast but technically useful introduction, read in this order:

1. `gpu-simulator/gpgpu-sim4.md` — overview of the 4.x performance model.
2. `gpu-simulator/accel-sim.cc` — trace-driven top-level control flow.
3. `gpu-simulator/trace-parser/trace_parser.{h,cc}` — trace representation and grammar.
4. `gpu-simulator/trace-driven/trace_driven.{h,cc}` — trace-to-timing bridge.
5. `gpgpu-sim/src/gpgpusim_entrypoint.cc` — execution-driven/PTX runtime flow.
6. `gpgpu-sim/src/abstract_hardware_model.{h,cc}` — warp instructions, memory transactions, coalescing.
7. `gpgpu-sim/src/gpgpu-sim/shader.{h,cc}` — SM core, schedulers, pipelines, execution units, LD/ST.
8. `gpgpu-sim/src/gpgpu-sim/scoreboard.*` and `stack.*` — dependencies and SIMT control flow.
9. `gpgpu-sim/src/gpgpu-sim/gpu-cache.*` — cache internals.
10. `gpgpu-sim/src/gpgpu-sim/mem_fetch.*` — memory-request lifecycle.
11. `gpgpu-sim/src/gpgpu-sim/icnt_wrapper.*` — network boundary.
12. `gpgpu-sim/src/gpgpu-sim/l2cache.*` — L2 and memory-subpartition plumbing.
13. `gpgpu-sim/src/gpgpu-sim/dram.*` / `dram_sched.*` — memory controller and DRAM.
14. `gpgpu-sim/src/gpgpu-sim/gpu-sim.*` — global cycle advancement and statistics.
15. `util/job_launching/run_simulations.py` — experiment orchestration.

This sequence follows the actual flow from workload input to instruction generation, SM timing, memory hierarchy, and experiment automation.
