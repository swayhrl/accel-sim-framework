# Validation summary

- Cold Core+Framework build: PASS.
- M1 directed test: PASS.
- G2-1/G2-2/G2-3/G2-4 directed tests: PASS.
- RTX3070 full LUD disabled/ideal transparency: PASS.  After removing only
  VM and host-rate fields, the logs have an empty diff; ideal reports 2,394
  identity translations and zero VM stalls.
- Same one-kernel, 10 GiB-bounded memory regression: disabled and functional
  both complete at 192,512 KiB RSS; no GiB-scale functional increment remains.
- Functional one-kernel replay: PASS, 9,522 cycles / 16,080 instructions;
  85 translation requests, 1 MSHR allocation, 1 walk start/completion, and
  waiter registrations/wakeups 1/1.  End state has zero active MSHR, PWQ, and
  walkers.

This closes M2-D and G2-4.  `G2-CLOSEOUT` remains required before M3.
