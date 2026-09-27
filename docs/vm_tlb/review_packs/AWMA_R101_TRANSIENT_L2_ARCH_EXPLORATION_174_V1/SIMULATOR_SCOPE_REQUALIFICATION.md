# Simulator L2/writeback scope requalification

Current status: `PREPARED_AWAITING_FORMAL_R101_INPUT`.

## Source audit (`VERIFIED_CODE`)

The accepted config uses:

`S:2048:128:16,L:B:m:L:X,A:192:4,32:0,32`

with eight memory channels and two subpartitions per channel. Thus the modeled
L2 has 16 instances, 128-byte lines, 2048 sets/instance and 16 ways, totaling
64 MiB and 524,288 lines.

The existing writeback path is real:

1. `tag_array::probe` chooses a legal LRU/FIFO victim subject to the existing
   dirty-line eligibility rule.
2. `tag_array::access` exports block address, dirty byte/sector masks and
   modified size in `evicted_block_info`.
3. `data_cache` allocates an `L2_WRBK_ACC` `mem_fetch` and places it in the
   finite miss/lower-memory queue.
4. the memory subpartition and DRAM model account writeback requests through
   ordinary queues and `n_wr_bk`/DRAM write statistics.

The narrow implementation points are therefore victim selection,
`evicted_block_info`, and the existing writeback enqueue function. No DRAM
latency/bandwidth, cache capacity, port, queue or translation parameter changes.

The exact kernel-completion hook is `gpgpu_sim::set_kernel_done`. Formal use is
restricted to the producer's one-stream ordered sequence; admission must prove
that the sidecar ordinal refers to this exact launch order.

## Completed qualification

- accepted pre-implementation VM/controller regressions: 3/3 PASS;
- candidate post-implementation regressions: 3/3 PASS;
- ten transient-policy directed tests: 10/10 PASS;
- complete unified binary build: PASS;
- default-OFF accepted T2 smoke: exact 93,079 cycles, 43,357,696 instructions,
  1,216 CTAs, 411,008 unique UIDs, untranslated/unobserved zero;
- no transient output when selector/diagnostics are absent.

## Still required before mechanism interpretation

- exact producer bundle admission and address intersection;
- B0 generation of real target-region dirty L2 writebacks;
- internal writeback/DRAM transaction and byte consistency;
- replay-scope scaling explanation against the ~346 MB Native/source anchor;
- terminal cache/memory and translation/controller drain.

Failure of these gates yields `R101_TRANSIENT_L2_SIM_MODEL_NOT_QUALIFIED`.
