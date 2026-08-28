# Corrected Conventional Sector-L2 Baseline v1 — Codex Implementation Handoff

> **Purpose**  
> This document is the implementation contract for the first L2 characterization stage.  
> The immediate goal is **not** to implement Decoupled-L2 / LateBind / AAD / token-based optimization.  
> The goal is to build a **clean, conventional, eager-allocation sector-L2 baseline** whose resource utilization and blocking behavior are sufficiently faithful that later workload characterization is not dominated by GPGPU-Sim's coarse cross-resource gates.

---

## 0. Non-negotiable execution contract

Codex must follow these constraints throughout this task.

1. **Do not start large-scale workload characterization before this baseline is closed out.**
2. **Do not add Decoupled-L2 mechanisms to the corrected baseline.**
   - No AAD.
   - No token allocator.
   - No delayed cache-line allocation.
   - No Decoupled-L2 lower-read credit scheme.
   - No Decoupled-L2 bank model.
   - No experimental WBQ ownership semantics.
3. The corrected baseline remains a **conventional sector cache with eager allocation on miss**:
   - probe tag;
   - choose/reserve set/way;
   - allocate/merge MSHR;
   - generate lower read and, if needed, dirty-victim writeback;
   - fill;
   - return merged requests.
4. Fix **artificial cross-resource coupling**, not real finite-resource backpressure.
5. Do not make a request proceed unless every resource that the request **actually needs at that point** is available.
6. Do not require unrelated resources to be free.
7. Preserve the official V100/QV100 cache organization, replacement policy, sector semantics, hashing, write policy and eager allocation unless this document explicitly says otherwise.
8. Existing experimental branches are **reference-only** for this task. Do not continue implementation directly on them.
9. All semantic changes must be individually reviewable and have a targeted test.
10. Do not use `git add .` or `git add -A`. Stage only explicit paths.
11. Do not force-push existing branches.
12. Record provenance, exact commits, config hashes and postcheck results.
13. If a proposed change would silently improve the baseline beyond the fidelity corrections defined here, do **not** implement it; document it as a follow-up sensitivity item.

---

# 1. Repositories, provenance and currently known revisions

## 1.1 Official reference points

### Accel-Sim framework

Repository:

```text
https://github.com/accel-sim/accel-sim-framework
```

Reference commit:

```text
3016c658f810bdae9a14bf4534ee99e9945eedae
```

### GPGPU-Sim core

Repository:

```text
https://github.com/accel-sim/gpgpu-sim_distribution
```

Reference commit:

```text
03c1fe443b1a46de695381662830bb4b9a4b3a00
```

This `03c1fe44` core is the publication provenance point for the corrected baseline.

---

## 1.2 Existing swayhrl experimental repositories

### Framework fork

```text
https://github.com/swayhrl/accel-sim-framework
```

Existing experimental branch:

```text
hrl/decoupled-l2-exp-v0
```

The previously recorded local pinned SHA was:

```text
6d6f8b20c89da0fcfaad5f3093fc4e186e76c39a
```

At the time of the audit, this SHA was not resolvable from the public GitHub branch.  
The public branch had moved forward; the public `hrl/decoupled-l2-exp-v0` HEAD observed during the audit was:

```text
13d2a135bdd08e9fac0cc468015cd3ec2dc20824
```

### GPGPU-Sim fork

```text
https://github.com/swayhrl/gpgpu-sim
```

Existing experimental branch:

```text
hrl/decoupled-l2-v0
```

The previously recorded local pinned SHA was:

```text
971edd97e0c6b6e5bdc246a6838db0841cbaa2a2
```

At the time of the audit, this SHA was not resolvable from public GitHub.  
The public branch HEAD observed during the audit was:

```text
4e6370aafa3623d55550ce04a149c879d0bd1457
```

That public HEAD is descended from / merged with the official reference:

```text
03c1fe443b1a46de695381662830bb4b9a4b3a00
```

### Required preflight

Before changing any source:

```bash
git remote -v
git status --short
git branch --show-current
git rev-parse HEAD
git cat-file -e 03c1fe443b1a46de695381662830bb4b9a4b3a00^{commit}
```

Also check whether the previously recorded local-only revisions still exist in any local reflog/worktree:

```bash
git cat-file -t 971edd97e0c6b6e5bdc246a6838db0841cbaa2a2 2>/dev/null || true
git reflog --all --date=iso | grep -F 971edd97 || true
```

Do the same in the framework for `6d6f8b20...`.

Record the result in:

```text
docs/l2_char/provenance.md
```

Do **not** reconstruct missing SHAs by guesswork.

---

## 1.3 Known audit conclusions from the currently public experimental core

The public `swayhrl/gpgpu-sim` revision inspected during preparation of this handoff used a selectable backend and showed the following behavior:

```text
baseline  -> instantiate original l2_cache
fixed     -> experimental backend
decoupled -> experimental backend
```

The public implementation dispatched:

```text
access_ready
next_access
waiting_for_fill
fill_port_free
fill
cycle
data_port_free
access
force_tag_access
```

to the original `l2_cache` whenever the experimental backend pointer was null.

The Decoupled-L2-specific lower-request FIFO reservation was guarded by a backend-dependent flag, and the baseline path fell back to the original:

```text
m_L2_dram_queue->full()
```

behavior.

**Audit result:** no obvious Decoupled-L2 AAD/token/lower-read/WBQ resource restriction was found leaking into the public `baseline` data path.

Therefore Codex should treat the old branch as a useful source for individually porting:

```text
dirty-victim forward progress
deadlock detection
diagnostic printing
additive statistics
```

but should **not** merge the branch wholesale.

The old public branch also still contained the same coarse official frontend gates that this handoff is intended to correct.

---

## 1.4 Compatibility handling for `-gpgpu_l2_backend`

The clean `03c1fe44` official base does not need the old three-way experimental backend selector.

Preferred rule for `hrl/l2-char-baseline-v1`:

```text
do not port Decoupled-L2 backend classes merely to preserve the old CLI flag
```

Use clean characterization config files that do not depend on the old selector.

If existing experiment infrastructure absolutely requires:

```text
-gpgpu_l2_backend baseline
```

Codex may add a **timing-neutral compatibility parser option** only if all of the following are true:

1. `baseline` is the only accepted/used backend in this branch;
2. it always instantiates the corrected conventional `l2_cache`;
3. no `decoupled_l2_cache` source or state is introduced;
4. the option is documented as a compatibility/provenance label only;
5. a run with the option omitted and a run with `-gpgpu_l2_backend baseline` are cycle/stat identical.

Future optimized branches may reintroduce a multi-backend selector **on top of this frozen corrected baseline**, but that is outside this task.

---

# 2. Branch and worktree strategy

The corrected characterization baseline must be separated from the old Decoupled-L2 experiment.

## 2.1 Core branch

Preferred new branch:

```text
hrl/l2-char-baseline-v1
```

Base it **directly** on:

```text
03c1fe443b1a46de695381662830bb4b9a4b3a00
```

Preferred safe workflow:

```bash
git fetch --all --prune

# From the swayhrl/gpgpu-sim repository:
git worktree add ../gpgpu-sim-l2-char 03c1fe443b1a46de695381662830bb4b9a4b3a00

cd ../gpgpu-sim-l2-char
git switch -c hrl/l2-char-baseline-v1
```

If that branch already exists, stop branch creation and inspect it. Do not overwrite it.

### Old core branch policy

Keep:

```text
hrl/decoupled-l2-v0
```

as a **read-only implementation reference**.

Do not merge the whole branch into `hrl/l2-char-baseline-v1`.

Only port individually audited fixes that are explicitly allowed by this document.

---

## 2.2 Framework branch

Preferred new branch:

```text
hrl/l2-char-exp-v1
```

Preferred provenance base:

```text
3016c658f810bdae9a14bf4534ee99e9945eedae
```

Preferred workflow:

```bash
git fetch --all --prune

git worktree add ../accel-sim-l2-char 3016c658f810bdae9a14bf4534ee99e9945eedae

cd ../accel-sim-l2-char
git switch -c hrl/l2-char-exp-v1
```

Do **not** wholesale merge `hrl/decoupled-l2-exp-v0`, because that branch currently contains a large amount of unrelated Decoupled-L2/C2P/trace-campaign material.

Port only minimal framework reliability fixes that are needed by the characterization campaign, each as a separate commit.

Candidate framework-side fixes to inspect and selectively port:

1. end-of-command-list cleanup guard in:
   ```text
   gpu-simulator/accel-sim.cc
   ```
2. trace parser copy/move ownership fixes and large-vector capacity release in:
   ```text
   gpu-simulator/trace-parser/trace_parser.cc
   gpu-simulator/trace-parser/trace_parser.h
   ```
3. trace-driven warp-vector capacity release in:
   ```text
   gpu-simulator/trace-driven/trace_driven.cc
   ```
4. NVBit capture reliability fixes only if new traces must be captured:
   ```text
   util/tracer_nvbit/...
   ```

Do not import unrelated experiment scripts or Decoupled-L2 configuration by default.

---

## 2.3 Commit discipline

Use small semantic commits. Recommended sequence:

```text
C0  docs: record L2 characterization provenance
C1  l2: add non-mutating request admission preview
C2  l2: remove coarse lower/response/data global admission gates
C3  l2: make MSHR and miss-queue admission exact
C4  mem: make DRAM return backpressure request-aware
C5  stats: add L2 resource and blocker observability
C6  stats: fix windowed sector-L2 miss accounting
C7  test: add corrected L2 synthetic regressions
C8  docs: freeze corrected conventional L2 resource model
```

For every commit:

```bash
git diff --check
git status --short
git diff --cached --stat
```

Stage explicit paths only, for example:

```bash
git add src/gpgpu-sim/l2cache.cc src/gpgpu-sim/l2cache.h
```

Never:

```bash
git add .
git add -A
```

---

# 3. Baseline semantics that must remain unchanged

The target is a corrected **conventional** sector-L2, not a new architecture.

For the QV100-style configuration under audit:

```text
-gpgpu_cache:dl2 S:32:128:24,L:B:m:L:P,A:192:4,32:0,32
-gpgpu_cache:dl2_texture_only 0
-gpgpu_dram_partition_queues 64:64:64:64
-gpgpu_l2_rop_latency 160
```

Interpretation:

```text
cache type                sector
sets                      32 per memory subpartition
line size                 128 B
associativity             24
capacity/subpartition     96 KiB
replacement               LRU
write policy              write-back
allocation                on miss / eager
write allocation          lazy fetch on read
set index                 IPOLY
MSHR                       192 entries
merge targets/MSHR        4
cache miss queue          32
data port width           32 B
partition FIFOs           64 / 64 / 64 / 64
```

With 32 memory channels and 2 subpartitions/channel, the configuration has 64 L2 subpartitions and an aggregate nominal L2 capacity of 6 MiB.

### Must remain true

A new conventional miss continues to reserve cache state eagerly:

```text
tag probe
   ↓
choose set/way
   ↓
reserve/allocate line or sector
   ↓
allocate/merge MSHR
   ↓
generate lower request(s)
```

Do **not** move allocation to fill time.

Do **not** add AAD-style address-only ownership.

Do **not** defer victim selection.

Do **not** add a Decoupled-L2 token stage.

---

# 4. Safe fixes that may be ported from the existing fork

## 4.1 Dirty-only replacement forward-progress fix

Reference implementation exists in the old core branch in:

```text
src/gpgpu-sim/gpu-cache.cc
```

The official implementation can incorrectly conflate:

```text
not an eligible clean victim
```

with:

```text
reserved / unavailable
```

when a positive dirty-ratio preference is active.

Correct semantics:

1. `all_reserved` is determined only by actual reserved state.
2. Clean victim preference is a replacement preference, not a resource-availability condition.
3. If no clean victim exists but an unreserved dirty victim exists, select the oldest dirty victim.

Keep:

```text
invalid victim
   > clean valid victim
   > dirty victim fallback
```

using the configured LRU/FIFO policy.

### Important QV100 note

For the audited QV100 L2, `m_wr_percent` defaults to zero and only the L1D write-ratio option is explicitly configured. Therefore the dirty-only fallback should normally be inert for the L2.

Still keep the correctness fix because:

- it is forward-progress safe;
- it prevents future positive-threshold configurations from falsely reporting all-reserved;
- it should not change normal QV100 L2 behavior.

Add a targeted unit regression for this case.

---

## 4.2 Deadlock detection fix

The existing fork changed deadlock progress detection away from only looking at global committed active-lane instruction count and toward the actual writeback/progress timestamp.

This is acceptable as a simulator correctness/diagnostic fix.

Port it separately.

It must not change normal naturally completing cycle behavior.

---

## 4.3 Deadlock diagnostics

The existing enhanced state dump is diagnostic only and may be ported separately.

It may include:

- L1/L2 tag-state summary;
- MSHR contents;
- miss queue occupancy;
- partition FIFO state;
- fail-reason counters;
- pipeline state.

Do not make diagnostics part of timing behavior.

---

## 4.4 Additive write-allocate statistics

Additive statistics that do not change the canonical HIT/MISS data path are acceptable.

Keep them additive and clearly named.

Do not redefine the core cache outcome merely to match a hardware counter.

---

# 5. P0 fidelity problem: coarse L2→DRAM queue gate

## 5.1 Existing problem

The old official `memory_sub_partition::cache_cycle()` uses a condition equivalent to:

```cpp
if (!m_L2_dram_queue->full() && !m_icnt_L2_queue->empty()) {
    // only then attempt a new L2 access
}
```

This incorrectly means:

```text
L2→DRAM queue full
       ↓
stop guaranteed L2 hits
stop MSHR merges
stop clean tag probes
stop write hits
stop accesses that generate no lower request
```

This is unacceptable for resource characterization.

## 5.2 Required change

Remove **L2→DRAM queue fullness as a global prerequisite** for attempting an input request.

Replace it with request-aware admission:

```text
inspect request without mutating state
          ↓
determine exact resources required
          ↓
only test the resources needed by this request
          ↓
commit access if available
```

The lower queue must block only requests that will actually enqueue one or more lower requests.

---

# 6. P0 fidelity problem: L2→ICNT response queue gate

## 6.1 Existing problem

The old controller effectively does:

```cpp
bool output_full = m_L2_icnt_queue->full();

if (!output_full && ...)
    m_L2cache->access(...);
```

This prevents misses and MSHR merges from entering when the response FIFO is full, even though they do not need an immediate upper response.

## 6.2 Required change

The response FIFO is required only when the current accepted access will immediately enqueue a response.

At minimum distinguish:

| Request outcome | Needs immediate L2→ICNT slot? |
|---|---:|
| read hit | yes |
| write-back write hit that returns ack upward | yes |
| L1 writeback absorbed locally | no |
| MSHR merge | no |
| new read miss | no |
| sector miss requiring lower read | no |
| dirty-victim miss | no immediate response |
| lazy-fetch write miss absorbed by L2 and immediately acknowledged | yes |
| fetch-on-write miss with lower read outstanding | normally no immediate response |

The exact result must be generated by the admission preview described below.

Do not use `m_L2_icnt_queue->full()` as a blanket frontend gate.

---

# 7. P0 fidelity problem: data-port gate

## 7.1 Existing problem

The old controller blocks every access when:

```text
data_port_free() == false
```

even though GPGPU-Sim's own bandwidth accounting already distinguishes:

- hit → data-port use;
- clean miss → no data-array transfer;
- dirty-victim miss → victim-data read for writeback;
- MSHR merge → no normal data read;
- reservation fail → no data use.

Therefore data-array pressure is currently allowed to become an artificial whole-L2 frontend stall.

## 7.2 Required change

Make data-port dependence request-aware.

Examples:

```text
read hit
    needs data port

write hit
    needs data port

MSHR merge
    does not need data port

new clean miss
    does not need data port

new dirty-victim miss
    needs data port for writeback victim data

sector miss with no victim writeback
    does not need data port at admission
```

### Important

Do **not** simply delete the `data_port_free()` check and call existing `access()`.

That would let a hit mutate/complete while the data port is busy and would over-model parallelism.

The controller must first perform a **non-mutating preview**, then admit only requests whose required resources are available.

---

# 8. Core implementation: non-mutating L2 access admission preview

This is the central implementation change.

## 8.1 Design requirement

Add a preview/planning interface that determines what the request would need **without**:

- updating LRU;
- changing line/sector state;
- allocating a line;
- allocating or merging an MSHR;
- changing dirty state;
- inserting miss-queue entries;
- generating cache-event side effects;
- incrementing normal hit/miss statistics.

Suggested names:

```cpp
enum class l2_block_reason;
struct l2_access_plan;
bool l2_cache::preview_access(..., l2_access_plan &plan) const;
```

Exact names may differ, but the split must be explicit:

```text
PREVIEW / PLAN
      ↓
ADMISSION CHECK
      ↓
COMMIT EXISTING ACCESS()
```

Do not duplicate the real cache-state mutation in the preview.

---

## 8.2 Suggested `l2_access_plan`

At minimum expose:

```cpp
struct l2_access_plan {
    cache_request_status probe_status;

    unsigned cache_index;

    bool is_read;
    bool is_write;

    bool mshr_hit;
    bool mshr_entry_available;
    bool mshr_merge_available;

    bool victim_valid;
    bool victim_dirty;
    unsigned victim_modified_bytes;

    unsigned new_missq_entries;

    bool needs_data_port;
    bool needs_fill_port;
    bool needs_immediate_response_slot;

    bool needs_new_mshr;
    bool needs_mshr_merge;

    bool will_send_lower_read;
    bool will_send_lower_write;
    bool will_send_writeback;

    bool l1_writeback_absorbed;

    // Optional diagnostics:
    uint64_t unsatisfied_resource_mask;
};
```

Use existing non-mutating primitives whenever possible:

```text
tag_array::probe(...)
mshr_table::probe(...)
mshr_table::full(...)
cache block status
access byte mask
access sector mask
write-allocate policy
```

Add const getters rather than exposing mutable internals.

Suggested safe additions:

```cpp
const cache_block_t *tag_array::get_block(unsigned idx) const;
unsigned mshr_table::num_entries_used() const;
unsigned mshr_table::num_targets_used() const;
bool mshr_table::response_ready(new_addr_type addr) const;
```

Do not let the characterization layer mutate tag/MSHR internals directly.

---

# 9. Exact resource planning for the QV100 baseline

The QV100 policy is:

```text
sector cache
write-back
allocate on miss
lazy fetch on read
```

This path must be implemented and tested first.

## 9.1 Read hit

```text
MSHR new entries       0
MissQ new entries      0
Data port              yes
Immediate RespQ        yes
Lower traffic          none
```

## 9.2 Read MSHR merge / HIT_RESERVED merge

```text
MSHR new entries       0
MSHR merge target      1
MissQ new entries      0
Data port              no
Immediate RespQ        no
Lower traffic          none
```

A full MissQ must **not** reject this request.

## 9.3 New clean read miss

```text
MSHR new entries       1
MissQ new entries      1 demand read
Data port              no at admission
Immediate RespQ        no
Lower traffic          1 read
```

## 9.4 New dirty-victim read miss

```text
MSHR new entries       1
MissQ new entries      2
                         1 demand read
                         1 victim writeback
Data port              yes for victim-data extraction
Immediate RespQ        no
```

## 9.5 Sector miss in an existing line

If no line replacement/writeback is generated:

```text
MSHR behavior          exact sector MSHR behavior
MissQ new entries      0 if merge
                       1 if new lower read
Data port              no at admission
Immediate RespQ        no
```

Do not charge a whole-line dirty victim unless the real existing access path would generate one.

## 9.6 Lazy-fetch-on-read write hit

For a normal write request:

```text
MissQ new entries      0
Data port              yes
Immediate RespQ        yes, unless this access type is explicitly consumed locally
Lower traffic          none
```

For `L1_WRBK_ACC` that is consumed locally, do not require an upper response slot.

## 9.7 Lazy-fetch-on-read write miss

This path is especially important.

A write miss may be absorbed into the cache without generating a lower read.

Therefore:

### clean/invalid victim

```text
MSHR                   normally none for a full write-validating sector
MissQ new entries      0
Data port              no unless existing access semantics require it
Immediate RespQ        yes for a normal upper write acknowledgement
```

### dirty victim

```text
MissQ new entries      1 victim writeback
Data port              yes for victim-data extraction
Immediate RespQ        yes for a normal upper write acknowledgement
```

A full MissQ must not block a lazy write miss that generates **zero** lower requests.

---

# 10. Preserve generic policies without silently breaking them

The main characterization target is QV100, but changes in shared `data_cache` code must not casually alter L1 or unrelated configs.

Preferred strategy:

1. Keep old behavior for L1 unless a change is independently justified.
2. Use:
   ```cpp
   m_level == L2_GPU_CACHE
   ```
   or an L2-specific wrapper/helper where needed.
3. Implement exact L2 planning for:
   - WRITE_BACK + LAZY_FETCH_ON_READ first;
   - then cover other existing write-allocate policies with targeted tests.

Expected exact lower-request counts:

### `NO_WRITE_ALLOCATE`

Write miss:

```text
1 lower write
```

### naive `WRITE_ALLOCATE`

Potential requests:

```text
1 original lower write
+ 1 lower read if new MSHR
+ 1 victim WB if dirty victim
```

If the lower read merges with an existing MSHR, do not charge a new read queue entry.

### `FETCH_ON_WRITE`

Full-sector/full-atom write:

```text
0 lower read
+ optional dirty victim WB
```

Partial write:

```text
0 lower read if MSHR merge
1 lower read if new MSHR
+ optional dirty victim WB
```

### `LAZY_FETCH_ON_READ`

As described above.

If generic-policy support becomes risky, keep the old path for non-QV100 policies and clearly mark them outside the characterization contract rather than inventing behavior.

---

# 11. Replace ambiguous MissQ capacity checks with exact checks

The existing helper:

```cpp
miss_queue_full(unsigned num_miss)
```

has non-obvious semantics and is frequently used as a conservative worst-case precheck.

Do not continue using it to describe exact new-entry requirements for corrected L2 admission.

Add an explicit helper such as:

```cpp
bool miss_queue_has_slots(unsigned n_new_entries) const {
    return m_miss_queue.size() + n_new_entries <=
           m_config.m_miss_queue_size;
}
```

or an equivalent safe implementation.

Then use **actual new entries**, not worst-case entries.

### Required read-miss ordering

Current coarse logic effectively checks MissQ before knowing whether the request can merge.

Correct ordering:

```text
probe tag
   ↓
compute MSHR address
   ↓
MSHR hit?
   ├── yes:
   │      check merge-target capacity only
   │      new MissQ entries = 0
   │
   └── no:
          check new-MSHR capacity
          inspect whether victim WB is required
          new MissQ entries =
              1 demand read
            + 1 if dirty victim WB
```

This is a P0 correction.

### Failure reasons

Preserve distinct fail reasons:

```text
MSHR_ENRTY_FAIL
MSHR_MERGE_ENRTY_FAIL
MISS_QUEUE_FULL
LINE_ALLOC_FAIL
MSHR_RW_PENDING
```

Do not collapse all failures into `RESERVATION_FAIL` in the new characterization counters.

---

# 12. Controller admission flow after correction

For each memory subpartition, keep a conservative baseline frontend width:

> **At most one new input request is admitted per subpartition per L2 cycle unless the official model already allows more.**

Do not increase frontend throughput as part of this fidelity fix.

Recommended flow:

```text
1. Drain ready MSHR responses if RespQ permits
2. Process DRAM-return/fill path
3. Drain one existing miss-queue request toward L2→DRAM if possible
4. Inspect head input request
5. Build l2_access_plan without mutation
6. Build unsatisfied-resource mask
7. If no required resource is blocked:
       call the existing real l2_cache->access()
       assert emitted events match the preview
       pop input according to existing semantics
   else:
       keep request in place and record blockers
8. Advance ROP latency path
```

### Plan/commit consistency assertions

In debug builds, after a successful commit, check:

```text
preview says lower read      ↔ emitted READ_REQUEST_SENT
preview says writeback       ↔ emitted WRITE_BACK_REQUEST_SENT
preview says lower write     ↔ emitted WRITE_REQUEST_SENT
preview missq count          ↔ actual newly inserted missq entries
```

If the preview and real access disagree, fail loudly in debug/testing.

Do not add silent fallback behavior.

---

# 13. DRAM issue correction: return-buffer backpressure must be request-aware

## 13.1 Existing problem

The old memory-partition arbitration uses the destination DRAM→L2 queue state as a generic gate for all outgoing requests.

That incorrectly blocks no-return writeback traffic when the return path is congested.

## 13.2 Modify the interface

Change from conceptually:

```cpp
bool can_issue_to_dram(int spid);
```

to:

```cpp
bool can_issue_to_dram(int spid, const mem_fetch *mf);
```

The arbitration loop must first inspect the head `mem_fetch`, then test resources appropriate to that request.

## 13.3 Define return-bearing vs no-return traffic

At minimum:

```text
L1_WRBK_ACC   no normal DRAM→L2 data return
L2_WRBK_ACC   no normal DRAM→L2 data return
```

Normal reads require return capacity.

Normal stores/write acknowledgements must preserve existing modeled return semantics and should not be reclassified without code-path proof.

Add a helper:

```cpp
bool requires_dram_to_l2_return(const mem_fetch *mf) const;
```

## 13.4 Required behavior

For a return-bearing request:

```text
need DRAM issue capacity
need normal arbitration credit
need return-path credit/capacity
```

For a no-return writeback:

```text
need DRAM issue capacity
need writeback/no-return issue credit
do NOT require dram_L2_queue space
```

The synthetic test `wb_when_returnq_full` must pass.

---

# 14. DRAM arbitration credit must not destroy WB forward progress

Merely removing the direct `dram_L2_queue_full()` gate may still leave writeback blocked if all generic arbitration credit is consumed by return-bearing requests.

Instrument this explicitly.

Add counters:

```text
wb_blocked_by_dram_credit_cycles
read_blocked_by_dram_credit_cycles
wb_issued_while_returnq_full
```

### Required forward-progress rule

Reserve at least one channel-level opportunity/credit for no-return writeback traffic so return-bearing reads cannot consume every admissible slot and indefinitely prevent a writeback that is required to release L2 capacity.

This is a **conventional forward-progress reservation**, not the Decoupled-L2 lower-read credit design.

Implementation options are acceptable if they satisfy all of these:

1. read traffic cannot consume the final no-return/WB progress credit;
2. WB still obeys actual DRAM scheduler fullness;
3. the reservation is per memory channel, not an arbitrary per-request unlimited bypass;
4. the size is explicit and configurable, with a default of one progress credit;
5. statistics report when the reservation is actually used.

Suggested option:

```text
-gpgpu_l2_wb_progress_credit 1
```

If Codex finds that existing private credits already guarantee the required synthetic case under all relevant states, document and prove it with a test instead of adding redundant state.

---

# 15. Do not silently change DRAM scheduler arbitration policy

While touching this loop, inspect the current use of:

```cpp
break;
```

when one candidate subpartition cannot push because `m_dram->full(mf->is_write())`.

Determine whether that `break` prevents trying another subpartition whose request class could be accepted.

If yes:

1. add a targeted regression;
2. change to `continue` only when this is a genuine cross-subpartition false HOL;
3. do not otherwise redesign FR-FCFS or channel arbitration.

Record this audit in:

```text
docs/l2_char/memory_partition_arbitration_audit.md
```

---

# 16. MSHR lifecycle: keep semantics in v1, but split the states in statistics

Do **not** change MSHR release timing in corrected-baseline v1.

The official model keeps an MSHR entry after fill while merged requests are being drained through the response path.

That creates two distinct MSHR states:

```text
A. memory-pending
   lower memory/fill not complete

B. response-ready
   fill complete
   one or more upper requests still waiting to drain
```

These must be measured separately.

Add getters/counters for at least:

```text
mshr_entries_total_used
mshr_targets_total_used

mshr_entries_memory_pending
mshr_targets_memory_pending

mshr_entries_response_ready
mshr_targets_response_ready

mshr_max_targets_on_one_entry
```

Also sample:

```text
mshr_merge_success
mshr_new_alloc_success
mshr_new_alloc_fail
mshr_merge_fail
```

### Why this matters

A high total MSHR occupancy is not automatically high miss concurrency.

If:

```text
mshr_response_ready
```

is large, the root cause may be response-network congestion.

Do not report only one aggregate MSHR-utilization number.

---

# 17. Fix the windowed miss-rate accounting bug

Audit and correct:

```text
tag_array::windowed_miss_rate()
tag_array::new_window()
```

The current implementation double-counts sector misses in the windowed rate and contains a redundant overwritten assignment.

Correct semantics:

```cpp
unsigned n_access =
    m_access - m_prev_snapshot_access;

unsigned n_miss =
    (m_miss + m_sector_miss) - m_prev_snapshot_miss;

float missrate =
    n_access ? (float)n_miss / n_access : 0.0f;
```

And:

```cpp
m_prev_snapshot_access = m_access;
m_prev_snapshot_miss = m_miss + m_sector_miss;
m_prev_snapshot_pending_hit = m_pending_hit;
```

Add a deterministic unit test with known:

```text
MISS
SECTOR_MISS
HIT
```

counts.

Do not use old windowed output for characterization results.

---

# 18. Characterization blocker statistics: define semantics precisely

Existing cache fail statistics count retries and cannot by themselves answer:

> how many distinct requests experienced a resource stall?

Add a separate L2 characterization statistics layer.

## 18.1 Required blocker categories

At minimum:

```text
L2_BLOCK_NONE

L2_BLOCK_LINE_ALLOC
L2_BLOCK_MSHR_NEW
L2_BLOCK_MSHR_MERGE
L2_BLOCK_MISSQ
L2_BLOCK_DATA_PORT
L2_BLOCK_RESPQ

L2_BLOCK_FILL_PORT
L2_BLOCK_RETURNQ

L2_BLOCK_DRAM_CREDIT
L2_BLOCK_DRAM_SCHED

L2_BLOCK_ROP_TO_INPUT

L2_BLOCK_OTHER
```

Do not label a lower queue as a "WBQ" unless it is actually a dedicated WBQ.

---

## 18.2 Record three distinct blocker metrics

For each reason record:

### A. blocker-cycle count

Every cycle a head request is blocked by that resource:

```text
blocked_cycles[reason]++
```

### B. request-ever-blocked count

For each request and reason, count once:

```text
requests_ever_blocked[reason]++
```

### C. blocking episodes

Increment when a request transitions from not blocked by reason X to blocked by X:

```text
blocking_episodes[reason]++
```

This separates:

- one request stalled 100 cycles;
- 100 requests stalled one cycle each.

---

## 18.3 Multiple simultaneous blockers

A request can require multiple unavailable resources.

Record:

```text
all_blocker_cycles[reason]
```

for every unsatisfied resource.

Also record one deterministic:

```text
primary_blocker_cycles[reason]
```

for causal summaries.

Recommended primary priority:

```text
1 line/set allocation
2 MSHR new/merge
3 MissQ
4 data port
5 response queue
6 downstream/DRAM
```

The exact priority may be adjusted, but document it and never change it silently between runs.

Prefer reporting both:

```text
all blockers
primary blocker
```

rather than pretending simultaneous constraints do not exist.

---

# 19. Per-request blocking state storage

Avoid adding timing semantics to `mem_fetch` only for statistics if possible.

Preferred implementation inside `memory_sub_partition`:

```cpp
struct l2_block_episode_state {
    uint64_t ever_blocked_mask;
    uint64_t prev_blocked_mask;
    uint64_t first_block_cycle;
    uint64_t total_block_cycles;
};

std::unordered_map<mem_fetch *, l2_block_episode_state>
    m_l2_block_state;
```

Create the entry when the request becomes the L2 input head or first experiences blocking.

Erase it when the request leaves the L2 frontend permanently.

Sector-split child `mem_fetch` objects are separate characterization requests unless an explicit parent aggregation metric is also recorded.

Do not leak entries after request completion.

Add an invariant at kernel end:

```text
no stale block-state entry for retired request
```

---

# 20. Resource utilization statistics to add before workload characterization

Sample at one consistent point per L2 clock for each subpartition.

Do not emit giant per-cycle traces by default.

Maintain:

```text
sum
max
nonzero_cycles
full_cycles
histogram / occupancy distribution
```

and optionally periodic windows.

## 20.1 Input / latency path

```text
ROP occupancy
ROP max occupancy
ROP ready-but-input-full cycles

ICNT→L2 queue occupancy
ICNT→L2 queue full cycles
```

## 20.2 Tag / cache state

```text
invalid lines/sectors
reserved lines/sectors
valid lines/sectors
modified lines/sectors

dirty-line ratio
reserved-line ratio

per-set:
    valid ways
    reserved ways
    dirty ways
    accesses
    misses
    reservation failures
```

Do not call these internal SRAM "banks".

The official model has L2 subpartitions but not a calibrated internal L2 data-bank organization.

## 20.3 MSHR

As defined above:

```text
total entries used
memory-pending entries
response-ready entries
total targets
pending targets
ready targets
merge depth histogram
```

## 20.4 Cache internal miss queue

Break down `m_miss_queue` by request class:

```text
demand read
normal lower write
L1 writeback
L2 writeback
write-allocate read
other
```

Report:

```text
total occupancy
WB-caused occupancy
demand-caused occupancy
full cycles
```

Use wording such as:

> shared lower-request / miss queue

not:

> WBQ

unless a true WBQ is added later.

## 20.5 L2→DRAM partition FIFO

Also classify:

```text
demand
WB
other write
```

## 20.6 DRAM→L2 return FIFO

Report:

```text
occupancy
full cycles
head-is-fill cycles
head-fill-blocked-by-fill-port cycles
```

## 20.7 L2→ICNT response FIFO

Report:

```text
occupancy
full cycles
MSHR-ready targets waiting while full
immediate-hit responses blocked
```

## 20.8 Ports

Report separately:

```text
data_port_busy_cycles
fill_port_busy_cycles
```

Also report accepted operation classes per cycle.

Do not combine data and fill port into one "L2 port utilization".

## 20.9 DRAM arbitration

Report:

```text
private/shared credit occupancy
read credit stalls
WB credit stalls
return-capacity stalls
DRAM scheduler-full stalls
WB issued with return queue full
```

---

# 21. ROP delay queue: instrument first, do not invent a capacity yet

The current ROP queue is a `std::queue` with a configured fixed latency and no explicit finite capacity.

Do not immediately choose an arbitrary hardware capacity.

First add:

```text
rop_occupancy_avg
rop_occupancy_p95
rop_occupancy_max
rop_ready_count
rop_ready_but_icnt_l2_full_cycles
rop_enqueue_count
rop_drain_count
```

### Required sensitivity gate

Run a small representative set after baseline fixes.

If ROP occupancy only behaves like a bounded latency pipeline and does not grow materially under downstream blocking, keep the existing model and document it.

If it grows far beyond latency × sustainable ingress rate because downstream backpressure cannot reach it, create a follow-up:

```text
Corrected L2 Baseline v1.1 — bounded ROP pipeline
```

Do **not** hide this issue.

Do not pick a queue size without a documented derivation or sensitivity sweep.

---

# 22. DRAM→L2 return FIFO HOL: instrument before structural redesign

Current return handling only inspects the FIFO head.

If the head is a fill and the fill port is unavailable, later non-fill responses may also be delayed.

Add:

```text
return_head_fill_wait_cycles
return_head_fill_wait_with_other_entries_cycles
return_head_fill_wait_with_nonfill_entries_cycles
```

A lightweight implementation can maintain parallel class counts on queue push/pop if the generic FIFO has no iterator.

### v1 rule

Do not automatically split the return FIFO unless measurements show material HOL.

If material, create a separate follow-up change with one of:

- separate fill and non-fill return classes;
- finite bypass/skid slot;
- documented response virtual channels.

Do not implement unlimited bypass.

---

# 23. Input FIFO HOL: measure it explicitly

The L2 input uses a head-of-line FIFO. A request blocked by:

- one set being reserved;
- one MSHR merge limit;
- one response requirement;

may prevent an independent request behind it from being examined.

This may be a real queueing assumption or an overly coarse model.

For v1:

1. preserve FIFO order;
2. record head blocking;
3. add optional diagnostic sampling sufficient to estimate whether independent work is trapped behind the head.

Do **not** add out-of-order request scheduling to the conventional baseline in this task.

If this becomes a major artifact, treat it as a separate sensitivity experiment.

---

# 24. Do not invent a dedicated WBQ in baseline v1

The official conventional cache places demand misses and generated writebacks into the shared internal miss/lower-request queue.

Therefore baseline-v1 characterization must report:

```text
shared lower-request queue occupancy
WB entries inside shared queue
WB-induced queue pressure
```

Do not report:

```text
WBQ utilization
```

for this model.

A dedicated finite WBQ may be introduced later only if:

1. the proposed research mechanism needs it;
2. the conventional reference design is explicitly defined;
3. its capacity is justified by literature/hardware sensitivity;
4. total buffering is accounted for fairly across designs.

---

# 25. Atomic-heavy workloads are a calibration/sensitivity class

GPGPU-Sim's atomic behavior is simplified.

Do not allow atomic-heavy graph/histogram workloads to dominate the first headline characterization without separate sanity checks.

Add per-workload metadata:

```text
atomic instruction count
atomic memory-request count
fraction of L2 traffic associated with atomic operations
```

Classify workloads as:

```text
normal
atomic-heavy
```

Atomic-heavy cases may remain in the suite, but headline resource claims must be robust without relying only on them.

---

# 26. Hash/set-mapping sensitivity

The QV100 L2 uses IPOLY set indexing.

Any claim such as:

> workload X has severe set-local pressure

must be accompanied by awareness that set pressure depends on the address→set mapping.

Keep IPOLY as the primary baseline.

Later sensitivity should support:

```text
IPOLY
linear
another plausible supported hash
```

Do not change the primary mapping during corrected-baseline closeout.

Add the mapping name and config string to every run manifest.

---

# 27. Synthetic regression suite — required before large runs

Create a deterministic corrected-L2 regression suite.

Preferred location:

```text
tests/l2_char/
```

or another project-consistent test location.

Prefer a deterministic C++ micro-harness or existing simulator unit-test framework.

Avoid production-only fault injection if the same state can be built with mocks/test fixtures.

## 27.1 Required tests

### T1 — `hit_under_lowerq_full`

State:

```text
L2→DRAM lower queue full
incoming request is guaranteed L2 hit
data port free
response slot available
```

Expected:

```text
hit is admitted
no lower request generated
```

Official coarse behavior would have blocked it.

---

### T2 — `miss_under_respq_full`

State:

```text
L2→ICNT response FIFO full
incoming request is a new clean miss
MSHR available
MissQ has one exact slot
```

Expected:

```text
miss admitted
new MSHR allocated
one lower read generated
no immediate response required
```

---

### T3 — `merge_under_missq_full`

State:

```text
existing outstanding same-sector MSHR
merge target available
MissQ full
```

Expected:

```text
merge succeeds
MissQ occupancy unchanged
no new lower request
```

---

### T4 — `clean_miss_one_slot`

State:

```text
new clean miss
exactly one MissQ slot available
```

Expected:

```text
admit
one lower read added
```

---

### T5 — `dirty_miss_one_slot`

State:

```text
new miss
dirty victim
only one MissQ slot available
```

Expected:

```text
block with MISSQ reason
no partial state mutation
```

Then with two slots available:

```text
admit
one lower read
one WB
```

---

### T6 — `data_busy_clean_miss`

State:

```text
data port occupied
incoming new clean miss
other resources available
```

Expected:

```text
clean miss can be admitted
```

---

### T7 — `data_busy_hit`

State:

```text
data port occupied
incoming hit
```

Expected:

```text
request blocks on DATA_PORT
tag/LRU/state unchanged
```

---

### T8 — `respq_full_hit`

State:

```text
response queue full
incoming hit
```

Expected:

```text
block on RESPQ
no hit completion/state mutation
```

If LRU-update timing is tied to accepted access, it must also not update while blocked.

---

### T9 — `l1_wb_under_respq_full`

State:

```text
L1_WRBK_ACC can be absorbed by L2
response queue full
```

Expected:

```text
do not block solely because RespQ is full
```

Preserve actual lower-WB requirements if the access evicts dirty L2 data.

---

### T10 — `wb_when_returnq_full`

State:

```text
DRAM→L2 return path full
head L2→DRAM request is L2_WRBK_ACC
DRAM scheduler can accept write
WB progress credit available
```

Expected:

```text
WB can issue
```

---

### T11 — `read_when_returnq_full`

Same state, but outgoing request needs a return.

Expected:

```text
read is blocked by return-path capacity
```

---

### T12 — `mshr_ready_split`

Create an MSHR, complete its fill, then prevent upper response drain.

Expected:

```text
total MSHR occupancy remains occupied under current baseline semantics
memory_pending decreases
response_ready increases
```

---

### T13 — `dirty_only_forward_progress`

Use a positive dirty threshold in a test-only cache configuration where a set has only unreserved dirty candidates.

Expected:

```text
oldest dirty victim selected
no false all-reserved / abort
```

---

### T14 — `windowed_sector_miss_rate`

Known sequence:

```text
2 HIT
1 MISS
1 SECTOR_MISS
```

Expected:

```text
window accesses = 4
window misses = 2
miss rate = 0.5
```

No double counting.

---

### T15 — `preview_commit_consistency`

For every covered request class:

```text
preview lower events == committed lower events
preview MissQ entry count == actual MissQ delta
preview response requirement == actual immediate response behavior
```

---

# 28. Official-vs-corrected equivalence campaign

Before characterization, run two arms:

```text
A = official 03c1fe44
B = corrected l2-char-baseline-v1
```

Use the same framework, trace, config and environment.

## 28.1 Low-pressure cases

Choose cases/configurations where none of the corrected coarse gates should trigger.

Require exact or explainable equality for:

```text
gpu_tot_sim_cycle
gpu_tot_sim_insn
L2 accesses
L2 hits
L2 misses
sector misses
DRAM reads
DRAM writes
writebacks
```

Also print:

```text
corrected_path_activation_count
```

If this count is zero, cycle behavior should be identical.

Any difference with zero corrected-path activation is a bug.

---

## 28.2 Pressure cases

For targeted cases where corrected gates intentionally activate:

Do not require official cycle equivalence.

Instead require:

```text
architectural completion identical
same instruction count
same memory values / functional result
no dropped request
no duplicate response
no MSHR leak
no request-tracker leak
```

and document the timing difference as intended fidelity correction.

---

# 29. Resource-model document to freeze before workload characterization

Create:

```text
docs/l2_char/L2_RESOURCE_MODEL.md
```

It must contain an implementation-derived diagram and table.

Required logical pipeline:

```text
SM / ICNT
   ↓
ROP latency path
   ↓
ICNT→L2 input FIFO
   ↓
Tag / lookup frontend
   ↓
 ┌──────────────┬───────────────────┬────────────────────┐
 │ HIT          │ MSHR MERGE        │ NEW MISS           │
 │              │                   │                    │
 ▼              ▼                   ▼                    │
Data Port     merge target      reserve line/sector      │
 │                                  │                    │
 ▼                                  ▼                    │
RespQ                           allocate MSHR             │
                                     │                    │
                               clean / dirty victim       │
                                │             │           │
                                ▼             ▼           │
                            demand read       WB          │
                                └──────┬──────┘           │
                                       ▼                  │
                                shared Miss/LowerQ        │
                                       ▼                  │
                                  L2→DRAM FIFO            │
                                       ▼                  │
                                    MC / HBM              │
                                       ▼                  │
                                 DRAM→L2 FIFO             │
                                       ▼                  │
                                    Fill Port             │
                                       ▼                  │
                                  MSHR ready state        │
                                       ▼                  │
                                    RespQ                 │
                                       ▼                  │
                                     ICNT                 │
```

Clearly mark:

### Explicitly modeled resources

```text
tag/set/way reservation
MSHR entries
MSHR merge targets
internal shared miss/lower-request queue
data port bandwidth
fill port bandwidth
four memory-subpartition FIFOs
DRAM arbitration credits
DRAM scheduler
response queue
ROP latency queue
```

### Not faithfully modeled / not to be claimed as measured hardware resources

```text
physical internal NVIDIA L2 SRAM bank count
real tag-bank count
real MSHR implementation details
real WBQ capacity
real NVIDIA slice pipeline widths
real response VC organization
```

---

# 30. Characterization output contract

After baseline closeout, every workload should produce one machine-readable summary, preferably JSON/CSV.

Required identity fields:

```text
framework_commit
core_commit
core_branch
l2_backend_name
gpu_config_sha256
trace/input identifier
trace sha256 if practical
kernel name
run command
```

Required L2 fields include at least:

```text
cycles

l2_accesses
l2_hits
l2_misses
l2_sector_misses
l2_pending_hits

data_port_util
fill_port_util

mshr_avg
mshr_p95
mshr_max
mshr_pending_avg
mshr_ready_avg
mshr_target_avg
mshr_merge_depth_p95

missq_avg
missq_p95
missq_max
missq_demand_avg
missq_wb_avg
missq_full_cycles

l2_dram_q_avg
dram_l2_q_avg
l2_icnt_q_avg
icnt_l2_q_avg

rop_avg
rop_p95
rop_max

dirty_ratio_avg
reserved_ratio_avg

block_cycles_<reason>
block_requests_<reason>
block_episodes_<reason>

dram_credit_stall_read
dram_credit_stall_wb
dram_return_stall
dram_sched_stall
```

Keep raw simulator native statistics as well; do not replace them.

---

# 31. Correct terminology for the paper

Do not describe this baseline as:

```text
unmodified official GPGPU-Sim baseline
```

Preferred term:

```text
Corrected Conventional Sector-L2 Baseline
```

or, when emphasizing revision alignment:

```text
same-revision corrected sector-L2 baseline
```

Suggested paper methodology wording:

> We derive the baseline from GPGPU-Sim commit `03c1fe44`, preserving its conventional sector-cache organization, eager allocation, replacement policy, and V100 configuration. We apply a small audited set of correctness and modeling-fidelity fixes that remove artificial cross-resource backpressure, provide writeback forward progress, and correct characterization statistics. All compared L2 designs use the same corrected simulator and memory-system revision.

Do not claim NVIDIA RTL equivalence.

---

# 32. Explicit non-goals for this branch

The following are **not** part of `hrl/l2-char-baseline-v1`:

```text
Decoupled-L2
LateBind
AAD
request token allocator
OTF table
new banked L2 architecture
adaptive MSHR partitioning
dynamic resource reallocation
new replacement policy
new prefetcher
new cache compression
new cross-SM sharing
new dedicated WBQ sized by guess
out-of-order L2 input scheduler
early-free MSHR redesign
bounded ROP redesign without evidence
return-VC redesign without evidence
```

These may be future optimization or sensitivity branches.

---

# 33. Branches after baseline closeout

Once corrected baseline passes all required tests:

Core:

```text
hrl/l2-char-baseline-v1
```

must become the frozen baseline implementation.

Tag or record its closeout commit in:

```text
docs/l2_char/provenance.md
```

Then create future mechanism branches **from this corrected baseline**, not from old Decoupled-L2:

```text
hrl/l2-resource-char-v1
hrl/l2-<future-mechanism>-v1
```

If characterization instrumentation is fully timing-neutral, it may live directly in the baseline branch. Otherwise put nontrivial instrumentation in:

```text
hrl/l2-resource-char-v1
```

and prove timing equivalence with instrumentation disabled.

Framework equivalent:

```text
hrl/l2-char-exp-v1
```

becomes the common workload/trace harness.

---

# 34. Required invariants and end-of-run assertions

Add or reuse assertions to guarantee:

```text
MSHR entries <= configured limit
MSHR targets/entry <= configured merge limit
MissQ occupancy <= configured limit

all accepted accesses are eventually retired
no request exists in two ownership locations illegally
no duplicate response
no dropped response

no stale preview/block-state entry after retirement
no negative DRAM credit
no credit returned twice

no dirty victim overwrite without WB event
no WB event without sufficient queue admission
no lower-read event without its MSHR/ownership state

preview event count == committed event count in debug mode
```

Assertions must expose the violating address/request and major queue occupancies.

---

# 35. Build and postcheck requirements

At each major commit:

```bash
git diff --check
```

Build the core/framework using the existing supported environment.

Record:

```text
build command
exit status
wall-clock start/end
compiler version
CUDA version
core commit
framework commit
```

For simulation regression record:

```text
run command
trace
config
exit status
gpu_tot_sim_cycle
gpu_tot_sim_insn
```

If a run hangs or stops making progress, capture the enhanced diagnostic dump before changing semantics.

Do not "fix" a failing test by increasing queue sizes unless the test is explicitly a capacity sensitivity test.

---

# 36. Review-pack requirement

At baseline closeout, create a review pack containing at least:

```text
docs/l2_char/provenance.md
docs/l2_char/CORRECTED_L2_BASELINE_V1.md
docs/l2_char/L2_RESOURCE_MODEL.md
docs/l2_char/memory_partition_arbitration_audit.md

synthetic test definitions
synthetic test results

official-vs-corrected comparison table

git log --oneline for the new branch
git diff 03c1fe44..HEAD --stat
git diff 03c1fe44..HEAD

relevant config files
postcheck logs
```

Package as:

```text
l2_corrected_baseline_v1_review_pack.tar.gz
```

Do not include giant build directories, full trace archives, or unrelated experiment outputs.

---

# 37. Suggested implementation file map

Expected core files:

```text
src/gpgpu-sim/gpu-cache.h
src/gpgpu-sim/gpu-cache.cc

src/gpgpu-sim/l2cache.h
src/gpgpu-sim/l2cache.cc

src/gpgpu-sim/gpu-sim.h
src/gpgpu-sim/gpu-sim.cc
```

Possible test files:

```text
tests/l2_char/...
```

Possible new characterization support:

```text
src/gpgpu-sim/l2-char-stats.h
src/gpgpu-sim/l2-char-stats.cc
```

A separate stats class is preferred if adding all counters directly to `memory_sub_partition` would make `l2cache.*` unreadable.

Do not modify broad unrelated code just to avoid adding a small L2-local helper.

---

# 38. Implementation order Codex must follow

## Phase A — provenance only

1. create clean worktrees;
2. create new branches;
3. record remotes/commits;
4. verify official QV100 config;
5. generate official-vs-existing-fork diff notes;
6. commit docs only.

No timing changes yet.

## Phase B — non-mutating preview

1. add const inspection APIs;
2. add `l2_access_plan`;
3. implement preview;
4. unit-test preview;
5. prove preview alone does not alter run timing/state.

## Phase C — controller gate correction

1. remove global lower-queue gate;
2. remove global response-queue gate;
3. remove global data-port gate;
4. replace all three with plan-based required-resource checks;
5. run T1/T2/T6/T7/T8/T9.

## Phase D — exact MSHR/MissQ

1. fix merge-under-MissQ behavior;
2. calculate exact queue-entry requirement;
3. keep L1 path unchanged unless independently tested;
4. run T3/T4/T5/T15.

## Phase E — memory partition

1. make return-path check request-aware;
2. guarantee no-return WB forward progress;
3. audit `break` vs `continue`;
4. run T10/T11.

## Phase F — statistics

1. split MSHR pending/ready state;
2. add occupancy/histograms;
3. add blocker cycle/request/episode stats;
4. add queue class breakdowns;
5. fix windowed miss rate;
6. run T12/T14.

## Phase G — closeout

1. full synthetic suite;
2. official-vs-corrected low-pressure equivalence;
3. targeted pressure cases;
4. freeze `L2_RESOURCE_MODEL.md`;
5. generate review pack;
6. push only the new branches.

Only after Phase G is PASS may large-scale characterization begin.

---

# 39. Acceptance criteria

The corrected baseline is **not closed** until all are true.

### Source/provenance

- [ ] core branch is based directly on `03c1fe44`
- [ ] framework provenance is documented
- [ ] old Decoupled branches were not merged wholesale
- [ ] every semantic patch has a focused commit

### Semantics

- [ ] conventional eager sector allocation preserved
- [ ] no Decoupled/AAD/token mechanism in baseline
- [ ] no global L2→DRAM gate on unrelated requests
- [ ] no global RespQ gate on misses/merges
- [ ] no global DataPort gate on clean misses/merges
- [ ] MSHR merges work when MissQ is full
- [ ] exact MissQ entry needs are enforced
- [ ] dirty-victim miss cannot partially allocate without WB space
- [ ] WB can make progress under return-path pressure

### Statistics

- [ ] windowed sector miss rate fixed
- [ ] MSHR pending vs response-ready separated
- [ ] distinct blocker cycles and blocked requests available
- [ ] shared lower queue broken down by demand/WB
- [ ] ROP occupancy visible
- [ ] return HOL visible
- [ ] DRAM credit stalls split by read/WB

### Tests

- [ ] T1–T15 pass
- [ ] zero-activation low-pressure corrected runs match official
- [ ] no request/credit/MSHR leak
- [ ] `git diff --check` clean
- [ ] build and run logs recorded

### Documentation

- [ ] `provenance.md`
- [ ] corrected-baseline design document
- [ ] resource model
- [ ] memory arbitration audit
- [ ] comparison results
- [ ] review pack

---

# 40. Final stop condition for Codex

After corrected-baseline closeout:

1. push:
   ```text
   hrl/l2-char-baseline-v1
   hrl/l2-char-exp-v1
   ```
2. provide:
   - final commit SHAs;
   - short commit log;
   - test summary;
   - official-vs-corrected comparison;
   - review-pack path;
   - list of unresolved model limitations.
3. **Stop before implementing the research optimization.**
4. **Stop before launching the full workload characterization campaign unless explicitly instructed to continue.**

The next stage will use this frozen baseline to characterize:

```text
set/way reservation pressure
MSHR entry and merge-target pressure
shared miss/lower-request queue pressure
writeback-induced pressure
data-port pressure
fill-port pressure
response-path pressure
ROP/input pressure
DRAM/downstream pressure
```

and only then decide which L2 resources should be decoupled, reallocated, enlarged, shared, or otherwise optimized.
