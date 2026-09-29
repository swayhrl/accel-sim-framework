# B0 UID1 coverage pilot (excluded from formal matrix)

Status: `NONFORMAL_SCOPE_PILOT_ONLY`.

This six-hour replay used the accepted full 18-kernel input and the frozen
none-mode transient-L2 implementation, but its inherited
`GPGPUSIM_VM_COVERAGE_KERNEL_UID=1` selector covered only runtime kernel UID1.
It therefore cannot qualify full-trace correctness and is excluded from every
B0/O1/M1 performance contrast.

Useful scope observations:

- cycles: 15,374,669;
- instructions: 6,195,889,164;
- CTAs: 46,860;
- L2 writeback: 2,531,000 requests / 323,967,936 bytes;
- target transient writeback: 2,530,987 requests / 323,966,336 bytes;
- DRAM writeback: 5,061,928 64-byte transactions / 323,963,392 bytes.

The pilot proves that the formal trace exercises real target-region dirty L2
writeback at the same order of magnitude as the accepted ~346 MB Native/source
anchor. It also exposed 29 requests still in printed DRAM latency queues and a
71-burst L2-to-DRAM accounting delta at exit. Those findings motivated the
matched opt-in terminal writeback drain used by the final formal matrix.

Durable raw root:

`/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/raw/pilot/B0_UID1_COVERAGE_20260927/`.
