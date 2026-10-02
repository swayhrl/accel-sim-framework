# Frozen online union and dispatch contract

Frozen before any M1 candidate timing for
`AWMA_R23G_R81_LIVE_DISPATCH_109_V1`.

Inputs are the current-step active XGrammar masks already resident on CPU as a
contiguous `torch.int32` tensor. Vocabulary size is exactly 151,936, hence each
row contains exactly 4,748 32-bit words and has no tail padding bits.

The only admitted implementation is:

1. expose the active CPU mask rows as a NumPy `uint32` view;
2. OR them across the row axis with `numpy.bitwise_or.reduce`, writing into one
   persistent preallocated `uint32[4748]` union buffer via `out=`;
3. view that buffer as bytes and index one persistent `uint8[256]` lookup table
   whose entry `i` is the exact population count of byte value `i`;
4. sum lookup results with a `uint64` accumulator to obtain exact union count;
5. divide by integer 151,936;
6. select A3 only when the fraction is strictly less than `0.01`; otherwise
   select A0.

`perf_counter_ns` separately brackets the OR, lookup-table popcount, and scalar
fraction/branch. Total union+dispatch time starts immediately before OR and ends
immediately after arm selection. All four values are recorded per step and are
inside M1's LIVE_HEAD wall boundary.

The persistent buffer and lookup table are created before timed generation.
There is no Python-set union, legal-ID union, GPU union, post-head ledger reuse,
threshold variation, or alternative implementation. The existing A0/A3 code,
including its duplicate internal mask unpack/legal-ID materialization, remains
unchanged for both B0 and M1.

