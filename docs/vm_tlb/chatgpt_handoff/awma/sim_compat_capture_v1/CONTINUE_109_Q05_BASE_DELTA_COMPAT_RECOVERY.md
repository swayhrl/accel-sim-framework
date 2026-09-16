# AWMA 109 V2 — Q05 base-delta compatibility recovery

## Authority

Continue from the pushed review checkpoint:

- execution branch: `hrl/awma-sim-compat-terminal-recovery-109-v2`
- checkpoint commit: `1cd8ccd83403265e89438fae4407ad0def7cb6c2`
- checkpoint status: `AWMA_ROUTE_B_Q05_CANARY_CHECKPOINT_REVIEW_REQUIRED`

Accepted consumer remains frozen at:

- `25aa29862239a408099639ae9d5f1a0ea4fee1e1`

Do not change the frozen workload/target identity and do not change node174 SIM baseline in this producer recovery.

## Review conclusion

The Q05 terminal/channel path is no longer the blocker. The exact Q05 canary naturally completed with terminal `COMPLETE`, `13,490,624` records, `drop_count=0`, and `overflow_count=0`.

The reported `ULDC.64` attribution is not accepted as the root cause. The preserved record

`0030 ffffffff 0 ULDC.64 0 0 0`

is a complete v5 non-MREF record under the frozen producer semantics. Do not fabricate a width or address for ULDC.

The actual compatibility defect to prove/fix is the legacy `base_delta` off-by-one contract:

- producer/Route-B encoder emits `base + (active_lanes - 1) deltas + immediate`;
- the frozen strict consumer parser and its old `trace_parser.cc` read `active_lanes` deltas before immediate;
- current upstream Accel-Sim parser uses the correct `active_lanes - 1` rule.

This explains `TRACEG_GRAMMAR_REJECT: missing immediate` on mode-2 records. Route-B `route_b_formatter_selftest.cc` already contains a two-active-lane mode-2 example that is sufficient to reproduce the mismatch without Q05.

## Chosen recovery policy

For this V2 producer closure, keep the frozen consumer/simulator unchanged. Avoid mode-2 `base_delta` in the formal producer encoding.

Use only canonical grammar modes already accepted by the frozen parser:

1. `base_stride` (mode 1) when losslessly applicable;
2. otherwise `list_all` (mode 0).

Do **not** emit mode 2 for this producer version.

This is an encoding-policy change only. It must not alter packet collection, dynamic instruction count, active mask, lane addresses, target identity, terminal semantics, or event ordering. XZ file compression may remain enabled.

The new producer source/binary hashes must be recorded normally.

## Execute as one solve-and-continue Goal

### R0 — CPU-only root-cause receipt

Before changing the formatter, use the existing Q05 trace and/or a minimal fixture to produce a bounded diagnostic receipt:

- show one failing mode-2 record;
- record active-lane count;
- show that the record has `N-1` deltas plus immediate;
- show that frozen strict parser consumes `N` deltas and therefore reports `missing immediate`;
- separately run a valid minimal trace containing only the preserved `ULDC.64 width=0` record and prove the frozen parser accepts that record semantics.

A diagnostic copy of the parser may add line/record context to the error message, but must not be used as the accepted parser and must not change acceptance semantics.

Record this as `BASE_DELTA_ROOT_CAUSE_CONFIRMED`.

### R1 — formatter policy patch

Modify the single shared Route-B raw formatter implementation, not a second copy.

Required behavior for `packet.is_mem`:

- calculate the effective active mask exactly as before;
- attempt existing `base_stride` compression;
- if successful: emit mode 1;
- if unsuccessful: emit mode 0 with every active lane address in lane order;
- never emit mode 2 in this V2 compatibility producer.

Do not change ULDC handling. `is_mem=false` remains width 0 and no address fields.

Add CPU tests covering at least:

- non-memory instruction with nonzero immediate;
- ULDC.64 / width 0 / no MREF;
- mode-1 memory record;
- irregular two-lane mask that previously selected mode 2 and must now select mode 0;
- irregular many-lane mask;
- nonzero immediate after a memory record;
- address arity equals effective active-mask population.

The test must pass the resulting traceg through the frozen `25aa...` `traceg_grammar_smoke`.

### R2 — one live tiny integration regression

Because lifecycle/B1 already passed, do not repeat broad B0/B1 archaeology.

Run one selected tiny live kernel after rebuilding the patched producer. It must prove:

- natural process exit;
- terminal COMPLETE;
- drop=0;
- overflow=0;
- receiver packet count == raw dynamic instruction count == strict-parser instruction count;
- post-processing succeeds;
- frozen exact consumer parser passes;
- no mode-2 records are present;
- at least one memory record is present.

If the tiny workload has only base-stride accesses, the CPU irregular-address tests above are the evidence for the mode-0 fallback.

### R3 — exact Q05 canary

Re-run the exact frozen Q05 target using the patched producer.

Identity remains:

- model: `Qwen/Qwen2.5-0.5B-Instruct`
- revision: `7ae557604adf67be50417f59c2c2f167def9a775`
- scenario: `S2_TEXT`
- phase: `PREFILL`
- batch: 1
- prefill_tokens: 2048
- decode_tokens: 32
- dtype: `float16`
- backend: `sdpa`
- target: `Q05_PREFILL_ATTN_FLASH`
- function occurrence: 0

Before launch, check free disk and set a conservative abort guard because mode-0 fallback may increase trace size. Do not weaken completeness if the guard is hit; fail closed and report measured growth.

Canary PASS requires:

- exact semantic/function/occurrence binding;
- natural terminal COMPLETE;
- zero drop/overflow;
- raw/postprocessed files close cleanly;
- no mode-2 records in final raw/traceg;
- frozen exact `25aa...` parser PASS;
- instruction count and CTA/warp structure close;
- source/build/binary/artifact hashes close.

### R4 — continue directly to formal producer closure

If R3 passes, do not stop for another ordinary milestone report. Continue the same Goal into the formal Q05 producer capture / qualification / accepted publication path required by the existing V2 Goal.

Complete:

- formal capture;
- terminal receipt;
- zero drop/overflow;
- kernelslist and member closure;
- parser closure;
- source/build/binary identities;
- trace/member/bundle hash roots;
- address context;
- accepted 109 -> durable storage / 174 READY publication;
- review pack and final producer report;
- commit, push, clean worktree.

Final producer success states remain:

- `SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS`
- `TERMINAL_PROTOCOL_SM89_RECOVERED_V2`

Then STOP node109.

## Prohibited shortcuts

Do not:

- fabricate ULDC addresses or memory width;
- derive width solely from `.64` for a packet with no MREF;
- patch the frozen consumer just to admit the trace;
- patch the frozen simulator baseline in this producer round;
- emit a dummy extra base-delta token to satisfy the old parser;
- convert C16WARP1/MREF into traceg;
- generate `SIM_INPUT_ID` on node109;
- run 10k simulation or mechanism sweeps on node109.

If another exact grammar incompatibility appears after mode 2 is removed, identify the first concrete failing record and solve it if it is an engineering encoding issue. Stop only if fixing it would require a real scientific/semantic contract change.
