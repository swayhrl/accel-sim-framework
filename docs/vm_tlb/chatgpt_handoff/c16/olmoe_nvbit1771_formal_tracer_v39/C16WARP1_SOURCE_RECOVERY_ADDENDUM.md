# V39 C16WARP1 source-recovery + schema-port addendum

This addendum removes the current V39 blocker. It is authoritative where it clarifies the provenance of the legacy C16WARP1 schema.

## Key finding

The old C16WARP1 producer source is present in Git history. It is **not binary-only**.

Exact historical authority branch/commit:

`hrl/c16-qwen3-s3-kv-scaling-109-v20@c94825dab9b114e468a83cdad009181f23add608`

Auditable source files:

`util/vm_tlb/c16/campaign/v20_warp_common.h`

`util/vm_tlb/c16/campaign/v20_warp_inject.cu`

`util/vm_tlb/c16/campaign/v20_warp_tool.cu`

Independent consumer/parser contract:

`util/vm_tlb/c16/analysis/c16_warp_container.py`

Additional formal consumer/audit implementation:

`util/vm_tlb/c16/q30_v3_audit_static_shards.py`

The node109 implementation worktree may not currently contain these paths because it is based on a different parent. Fetch/read them explicitly from the exact historical commit with `git show`, or create a temporary read-only worktree. Do not assume their absence from the current worktree means the source is lost.

## Important correction: old V20 did not use the missing receiver lifecycle

The V20 C16WARP1 source does **not** define a manual receiver thread that V39 needs to recover.

Its implementation is:

`instrumented device helper -> managed WState/WRec buffer -> selected launch exit synchronization -> direct host binary write -> stdout terminal receipt`

Therefore:

- use V20 source as **event/wire/terminal semantic authority**
- use the already-proven official NVBit 1.7.7.1 mem_trace scaffold as **lifecycle/channel/receiver authority**
- do NOT try to reconstruct a nonexistent V20 receiver lifecycle
- do NOT import the V20 1.7.5 context/global lifecycle

## Exact legacy C16WARP1 wire contract

From the source and independent parser:

### Header

Little-endian:

`<8sIIQQQ`

Fields in order:

1. magic: 8 bytes = `C16WARP1`
2. selected static index: uint32
3. selected function occurrence: uint32
4. callback/produced warp-record count: uint64
5. overflow count: uint64
6. records written/kept: uint64

Header size must be derived from the struct definition, not hardcoded by guess.

### Record

Little-endian:

`<6I32Q`

Exactly 280 bytes.

Fields:

1. `static_index` uint32
2. `active_mask` uint32
3. `cta_x` uint32
4. `cta_y` uint32
5. `cta_z` uint32
6. `warp` uint32
7. `addr[32]` uint64[32]

The active mask defines which lane addresses are scientifically active; inactive-lane array entries are not events.

### Exact terminal stdout contract

Historical producer prints:

`C16_WARP_TERMINAL static=<static> occurrence=<occ> records=<count> overflow=<overflow>`

The accepted parser requires exactly one matching terminal record and requires its tuple to agree with the binary header.

## Exact formal closure rules already enforced by consumer source

The current accepted consumer parser `c16_warp_container.py` validates:

- magic == `C16WARP1`
- header static index == expected selected static
- header occurrence == expected occurrence
- exact file size = header + records_written * 280
- overflow == 0
- callback_records == records_written
- every record's static_index == selected static
- exactly one terminal stdout match
- terminal tuple == (static, occurrence, records_written, overflow)

Only after those checks may:
- `records_written > 0` => `EXECUTED_SHARD`
- `records_written == 0` => `ZERO_EXECUTION_PROVEN`

Thus V38-style missing output/terminal can never be accepted as zero execution.

## "drop" semantics

The historical C16WARP1 binary header has **no independent drop field**.

Do not invent one.

For compatibility text/receipts:
- `overflow=0` is a real wire/header field
- `callback_records == records_written` is a real consumer closure check
- exact terminal agreement is a real closure check

If a V39 review receipt wants to state `drop=0`, it must label it as a **derived no-unaccounted-records condition**, not a raw C16WARP1 wire field, and define it from a source-backed producer/receiver counter equality.

Because the new 1.7.7.1 implementation uses an official channel/receiver lifecycle rather than the old managed buffer, V39 must add explicit producer-vs-receiver accounting:

- device/producer emitted-record counter
- host receiver accepted/written-record counter
- any channel overflow/drop counter exposed by the implementation
- terminal sentinel/receiver terminal state

Formal closure requires:
- producer emitted == receiver accepted == C16WARP1 records_written
- channel/receiver drop == 0
- overflow == 0
- terminal received exactly once
- binary header and stdout/sidecar terminal agree

If NVBit Channel has no directly queryable drop counter, do not manufacture one. Prove no unaccounted records by independent producer and receiver counters, and label the receipt accordingly.

## Porting policy for V39

Continue the current official NVBit 1.7.7.1 context-owned/channel/receiver implementation.

Port from V20 only:

- WRec scientific fields
- warp active-mask semantics
- CTA/warp identity semantics
- source-register-derived lane address semantics
- C16WARP1 on-disk header/record layout
- exact terminal text semantics
- selected static / occurrence meaning
- overflow/capacity meaning

Do NOT port:

- old 1.7.5 global state
- old lifecycle
- old managed-buffer ownership model merely for compatibility
- old context teardown behavior

The new receiver may internally use a different packet/envelope as required by the official 1.7.7.1 channel, but the finalized formal shard must serialize to the exact C16WARP1 contract above and pass the existing independent parser unchanged.

## Required golden compatibility tests before OLMoE canary

### G0 — parser regression on historical accepted artifact

Take at least one historical accepted C16WARP1 shard and run the exact current independent parser.

Record PASS and parser source/hash.

### G1 — new 1.7.7.1 nonzero fixture

Generate a new bounded selected-memory fixture through the new 1.7.7.1 tracer.

Require the existing parser, **without compatibility relaxation**, to accept:
- header
- records
- terminal
- no overflow
- producer/receiver count closure

### G2 — new 1.7.7.1 true zero-execution fixture

Select a statically valid instruction/occurrence proven not to execute while the tracer lifecycle itself closes.

Require:
- valid C16WARP1 binary exists
- callback_records = 0
- records_written = 0
- overflow = 0
- exact terminal exists
- producer/receiver counters close
- existing parser classifies `ZERO_EXECUTION_PROVEN`

### G3 — negative regression

At minimum prove the parser rejects:
- missing terminal
- terminal/header count mismatch
- overflow != 0
- callback_records != records_written
- truncated/trailing binary

Do not relax the parser to make the new producer pass.

## V39 continuation

After source recovery and G0-G3 PASS, resume the existing V39 plan at:

`regenerate exact actual-A 1096 static instructions -> 243-row selector/hash closure -> formal-protocol A probes -> typed canaries -> complete 243-shard formal capture -> serial admission/positive ACK`

Do not create a new scientific target.

Do not start a new V40 merely because the source was in another Git branch.

## Required new review evidence

Add to the V39 review pack:

- `C16WARP1_SOURCE_AUTHORITY.json`
- `C16WARP1_SCHEMA_CONTRACT.md`
- `C16WARP1_GOLDEN_COMPATIBILITY.json`
- `C16WARP1_NEGATIVE_REGRESSION.json`
- producer/receiver accounting definition and receipts

The source-authority receipt must bind:
- historical branch + commit
- all four source/parser paths above
- their local SHA256 after retrieval
- distinction between legacy semantic authority and new 1.7.7.1 lifecycle authority
