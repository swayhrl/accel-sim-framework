# EP-L2 Target Baseline v0 — Source-to-Structure Map

## Scope and evidence

This is a source audit, not an implementation or performance result.  It maps
the target-baseline contract in
[`ELASTIC_PAYLOAD_L2_ARCHITECTURE_AND_ROADMAP.md`](ELASTIC_PAYLOAD_L2_ARCHITECTURE_AND_ROADMAP.md)
and [`EP_L2_CODEX_NEXT_STAGE_HANDOFF.md`](EP_L2_CODEX_NEXT_STAGE_HANDOFF.md)
to the frozen simulator.  `VERIFIED` denotes behavior read in that source;
`TARGET_SPEC` denotes the supplied design; `PROPOSAL` is an implementation
location only, not a claimed existing behavior; and `OPEN` links to the
decision register.

| repository | worktree | branch | HEAD | state at audit start |
|---|---|---|---|---|
| Framework | `/workspace/worktrees/accel-sim-ep-l2` | `hrl/ep-l2-exp-v0` | `d24455a1981d7f099f641b5b6f17adb08d973a4a` | clean except the supplied `docs/ep_l2/` inputs |
| Core | `/workspace/worktrees/gpgpu-sim-ep-l2` | `hrl/ep-l2-target-baseline-v0` | `32f9b8d52490044f487c14811121ed0368e48a48` | clean |

The active-core conclusion is `VERIFIED`: the existing Framework runner
[`util/l2_char/run_round1_campaign.py`](../../util/l2_char/run_round1_campaign.py#L176)
sources its explicit `--core` argument before it sources the Framework setup
script.  The latter otherwise clones/uses `$ACCELSIM_ROOT/gpgpu-sim`
([`gpu-simulator/setup_environment.sh`](../../gpu-simulator/setup_environment.sh#L93)).
Consequently a future EP-L2 runner must pass
`/workspace/worktrees/gpgpu-sim-ep-l2` explicitly; it must not silently use a
Framework-local `dev` clone.

## Verified current request lifecycle

The current path has one address-indexed MSHR object and a distinct, short
lower-issue queue:

```text
ICNT→L2 FIFO
  → memory_sub_partition::cache_cycle()
  → l2_cache::preview_access()/access()
  → tag_array + mshr_table
  → baseline_cache::m_miss_queue
  → L2interface → per-subpartition L2→DRAM FIFO
  → memory_partition_unit arbitration/DRAM
  → DRAM internal returnq → per-subpartition DRAM→L2 FIFO
  → baseline_cache::fill()
  → tag_array::fill() + mshr_table::mark_ready()
  → mshr_table::next_access() completes waiters
```

Evidence:

* `memory_sub_partition` owns the four FIFO objects and constructs them from
  `-gpgpu_dram_partition_queues` in
  [`l2cache.cc`](../../../gpgpu-sim-ep-l2/src/gpgpu-sim/l2cache.cc#L767).
* A new read is appended to the MSHR and then inserted into `m_miss_queue` in
  [`gpu-cache.cc`](../../../gpgpu-sim-ep-l2/src/gpgpu-sim/gpu-cache.cc#L1515).
* `baseline_cache::cycle()` pops `m_miss_queue` as soon as its memport accepts
  the request ([`gpu-cache.cc`](../../../gpgpu-sim-ep-l2/src/gpgpu-sim/gpu-cache.cc#L1350)).
  It therefore **does not** have target-descriptor lifetime.
* The response restores the original request, fills the tag array, marks its
  MSHR entry ready, and then removes the extra request record
  ([`gpu-cache.cc`](../../../gpgpu-sim-ep-l2/src/gpgpu-sim/gpu-cache.cc#L1390)).
  `mshr_table::next_access()` releases the address entry only after its waiter
  list drains ([`gpu-cache.cc`](../../../gpgpu-sim-ep-l2/src/gpgpu-sim/gpu-cache.cc#L727)).

This provides a useful completion-path template but is not the target
structure: target `descriptor` ownership must outlive lower issue and be
bounded globally at 256.

## Resource map

| Target resource | Current object and evidence | Current allocation / release / blocker | Mapping status and required treatment |
|---|---|---|---|
| 64 slices, 32 channels, 2 slices/channel | `-gpgpu_n_mem 32` and `-gpgpu_n_sub_partition_per_mchannel 2` in `configs/tested-cfgs/SM7_QV100/gpgpusim.config`; options registered in `src/gpgpu-sim/gpu-sim.cc:260-265` | `memory_sub_partition` is one L2 slice. | `VERIFIED`, config-only; retain unless an EP-L2 target overlay explicitly changes it. |
| L2 resident tag: 64 sets × 16 ways × 128 B | `cache_config::init()` parses the `dl2` string (`gpu-cache.h:577-757`); `tag_array::m_lines` is indexed as set × way (`gpu-cache.h:1024-1049`). | `tag_array::access()` allocates a victim on a miss; `fill()` turns the same line valid; `RESERVATION_FAIL` means every candidate way is reserved (`gpu-cache.cc:305-480`). | Geometry is `VERIFIED` config-only (`S:64:128:16,...`). `RESOLVED`: retain four 32-B sectors, while Tag/Payload/WAD/MSHR indexing is one 128-B line. No payload-pointer semantics exist. |
| 1024 resident payload entries | No independently allocated payload array exists.  `cache_block_t` combines block address, tag, state and dirty metadata (`gpu-cache.h:133-178`); actual data bytes are not modelled separately. | A resident line's apparent data lifetime is coupled to `tag_array` line allocation/fill/eviction. | `TARGET_SPEC` requires a new explicit payload owner/state model. `PROPOSAL`: a per-`l2_cache` payload component, initially quota-limited to IDs 0–1023. |
| 128 bypass-only payload entries | No current L2 bypass-return payload store or role exists.  `memory_sub_partition` only routes `mem_fetch` objects through FIFOs (`l2cache.h:343-395`). | N/A. | `TARGET_SPEC`; new semantics and new state are required. |
| B0-Legacy: two 1R1W RAMs | Current `bandwidth_management` has independent occupancy counters called DataPort and FillPort. A hit or WB read consumes `m_data_port_occupied_cycles`; a fill consumes `m_fill_port_occupied_cycles` (`gpu-cache.cc:1281-1348`). | These counters block only their current call sites; they are not two explicit resident/bypass arrays and do not identify the requested EP-L2 operation classes. | `TARGET_SPEC`; code change. Do not relabel L2CHAR DataPort/FillPort as B0 ports. |
| B0-Banked: 4 × 288, one arbitrary 128-B op/bank/cycle | No L2 payload-bank state or per-bank arbitration exists.  `l1_banks` is L1-only. | N/A. | `TARGET_SPEC`; new code. The static 1024/128 ownership rule must remain in B0-Banked. |
| 128 line MSHRs | `baseline_cache::m_mshrs` is an `mshr_table`, constructed from `m_mshr_entries` (`gpu-cache.h:1330-1502`). | New block address consumes a hash-table entry; address full is `m_data.size() >= m_num_entries` (`gpu-cache.cc:632-654`). | `VERIFIED` config capacity can become 128, but the full target model needs the descriptor change below. |
| 256 globally shared persistent descriptors | C3 adds a free-list-backed descriptor pool and descriptor-ID chains in `mshr_table`; the old `mshr_entry::m_list<mem_fetch*>` is retained solely as a compatibility/request-ownership mirror. | Descriptor allocation is global (≤256), chain allocation is ≤32/line, and `commit_next_access()` releases only after L2→ICNT enqueue. `m_miss_queue` remains the short lower-issue queue. | `IMPLEMENTED C3`; the `m_list` mirror is not target physical storage and must not become a second resource authority. |
| 32 descriptors/address | Current `m_mshr_max_merge`; `mshr_table::full(addr)` applies it to the one address list (`gpu-cache.cc:641-648`). | Per-address merge failure occurs once this list reaches the configured maximum. | The cap is a reusable semantic, but `A:128:32` would permit 4,096 total waiters. `TARGET_SPEC` therefore needs the new pool to enforce **both** global ≤256 and chain ≤32. |
| Descriptor lifetime through requester completion | Current MSHR waiter list survives lower issue and is drained after `mark_ready()`. `m_miss_queue`, conversely, drains at lower acceptance. | See lifecycle above. | `RESOLVED`: new descriptor lifetime ends only after its requester response has successfully entered L2→ICNT. |
| WAD: 128 line-address entries, released at WB response | No line-address WAD/WBQ map exists. `tag_array::pending_lines` is a small address→instruction-UID helper, not a WB state machine (`gpu-cache.cc:287-303`). `wb_addr` is initialized but is not a tracker. | Existing WB is a new `mem_fetch` generated on dirty eviction (`gpu-cache.cc:2055-2069`). Writebacks are no-return DRAM requests (`l2cache.cc:444-476`) and retire through `set_done()` (`l2cache.cc:684-695`). | `TARGET_SPEC`; new address-indexed table and an explicit simulator-equivalent WB completion event are required. Do not treat the current forward-progress credit as a WAD. |
| L2→DRAM FIFO: 128 per slice | The second field of `-gpgpu_dram_partition_queues` becomes `m_L2_dram_queue` (`l2cache.cc:767-776`); current QV100 is `64:64:64:64`. | `L2interface::full/push` gates lower issue (`l2cache.h:379-395`); partition arbitration later pops it. | `VERIFIED`, config-only: overlay field 2 = 128. |
| FR-FCFS queue: 128 per channel | `-gpgpu_frfcfs_dram_sched_queue_size` is registered as “entries per chip” (`gpu-sim.cc:274-279`) and `dram_t::full()` applies it to the FR-FCFS pending queue (`dram.cc:164-195`). | Enqueue/issue are owned by `dram_t`/`frfcfs_scheduler`. | `VERIFIED`, config-only: set to 128. “Chip” corresponds to this model's memory-channel object; record the scope in manifests. |
| DRAM ReturnQ: 192 per channel | `dram_t` constructs internal `returnq` from `-gpgpu_dram_return_queue_size` (`dram.cc:118-127`). | `memory_partition_unit::dram_cycle()` moves it to a destination subpartition's `m_dram_L2_queue` only when the latter is not full (`l2cache.cc:582-608`). | `RESOLVED`: set internal ReturnQ=192/channel and retain separate DRAM→L2=64/slice, with separate statistics. |
| 850 MHz / 1 GHz DRAM variants | `-gpgpu_clock_domains` sets the DRAM clock; current QV100 is 850 MHz. | Clock-domain parsing is configuration-level. | `RESOLVED`: 850 MHz primary; 1 GHz sensitivity only. |
| L1 primary: 64 KiB, 4 sets, 128 ways, 128 B, 4 banks, 20 cycles | Current QV100 L1 is `S:4:128:64,...A:512:8,16:0,32`, 4 banks, 20-cycle latency. Options are registered in `gpu-sim.cc:381-400`. The per-bank latency pipe admits at most one request/bank/cycle (`shader.cc:2068-2106`). | Current L1 has 512 MSHR entries, 8 fixed merges/address, MissQ 16, write-through, on-miss allocation, lazy fetch on read. Adaptive L1 can also change associativity per kernel (`shader.cc:3584-3628`). | `RESOLVED`: config `S:4:128:128` while retaining those QV100 internals; disable adaptive reassociation and assert fixed associativity. |
| Existing characterisation | Core emits `L2CHARV1` from `l2-char-stats.*` and Framework parser accepts only that schema (`util/l2_char/parse_l2_char.py`). | Its MSHR-target, MissQ and DataPort/FillPort fields have conventional-model definitions. | `VERIFIED`; retain it unchanged. EP-L2 target instrumentation must be a separate `EPL2B0V1` record family and parser path. |

## Required target-baseline invariants, mapped to enforcement sites

The following are target requirements, not claims about current code.  They
define the minimum code/test surface once the pending decisions are frozen.

| Invariant | Existing related path | Enforcement proposal |
|---|---|---|
| line MSHRs ≤128; descriptors ≤256; a descriptor belongs to exactly one chain; chain ≤32 | `mshr_table::add/full()` | New pool allocator and per-line chain object; assert on allocate, append, detach and free. |
| lower issue never frees descriptor | `baseline_cache::cycle()` currently only pops the short MissQ | Keep descriptor allocation outside `m_miss_queue`; assert descriptor owner remains live after `m_memport->push()`. |
| one requester completion, then descriptor free | `mshr_table::next_access()` | Make completion path consume exactly one descriptor; terminal audit checks free-list cardinality. |
| response cannot write a reused tag/payload | `baseline_cache::fill()` currently uses `m_extra_mf_fields[mf]` and direct cache index | Add payload/generation ownership token to the lower transaction; gate any tag attachment on address + generation + owner match. |
| mandatory WB cannot be displaced by opportunistic state | current WB credit only protects lower issue | WAD allocation must precede destructive dirty-victim mutation; priority reclaim must never reclaim pending/inflight WB entries. |
| B0 bank service is bounded and lossless | no counterpart | Per-bank one-op grant per cycle; queued/retried operation is observable; assertion counts grants ≤1/bank/cycle. |
| all target resource pools drain at termination | `l2_char_no_resource_leak()` covers only old queues/MSHRs | Extend a separate EP-L2 terminal invariant with MSHR, descriptor, payload, WAD and bank-operation state. |

## Consequence for implementation order

The configuration-only layer can define the L2 geometry, L1 geometry (once
frozen), lower FIFO, scheduler, return queue and two DRAM frequency overlays.
It cannot establish B0 correctness by itself.  The first non-configurable
semantic boundary is the replacement of fixed per-MSHR waiter lists with
`128 line entries + one 256-entry persistent descriptor pool`; the next is
explicit payload/WAD state.  No RO pending, TVD hit, dynamic payload borrowing
or graphics-bypass mechanism is included in this audit's proposed B0 scope.
