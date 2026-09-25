# Pre-L1 exact coalescer RTL proxy

This directory contains a technology-neutral, synthesizable proxy for the
frozen `PREL1_EXACT_TRANSLATION_REQUEST_COALESCER` contract.

It implements only:

- two exact-key CAM entries;
- FREE/LIVE/DRAIN state;
- 32 bounded waiter continuations per entry;
- deterministic entry-full and waiter-full fallback signals;
- leader completion-tag matching;
- finite follower drain and entry reuse.

It intentionally does not implement a TLB, PTW, scheduler or GPU memory
pipeline. The one-follower-per-cycle drain is a conservative proxy interface,
not a claim that the performance simulator modeled that delivery bandwidth.

Parameters use source-visible simulator widths by default: ASID 32, significant
VPN 33 for 49-bit VA/64KiB pages, generation 64, access class 2, request tag 32
and PPN 33. ASID/generation hardware widths remain paper design assumptions.

`REGISTER_COMPARE=0` represents the simulator's same-cycle compare assumption.
`REGISTER_COMPARE=1` inserts an input request register and represents the
pre-registered +1-cycle structural variant. `WAITER_META_W=32` is the minimum
source UID continuation proxy; `WAITER_META_W=325` is the documented
conservative request-metadata proxy.

Correctness:

```bash
./run_tests.sh
```

Generic synthesis:

```bash
./run_synthesis.sh
```

Yosys/ABC results are `TECHNOLOGY_PROXY_ONLY`; no project-approved standard
cell library is available, so these results are not GPU area or Fmax claims.
