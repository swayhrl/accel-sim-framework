# Accepted850 absolute performance frontier

The machine-readable frontier reuses111 finite EP endpoints over27 exact inputs in Source78, plus two separately labeled diagnostic witnesses and four separateSource92 endpoints. Per-input best configurations are not a uniform hardware design. All45 earlier system-pair small spec/point/archive references were rechecked; no Trace/raw was scanned.

Key accepted witnesses:
- Conv REF F335088 -> G64x16 F291469:1.1497x absolute speedup,13.02% fewer cycles. Matched S331234 ->292932:1.1308x,11.56% fewer cycles. Same-background S/F is only1.0050x.
- Conv G64x16 plus UD2 queues gives F291522, slightly worse than pure geometry291469. More queues are not automatically useful.
- Vector4M FRFCFS256 F77237 ->74098:1.0424x,4.06% fewer cycles. S77184 ->73895 also improves; this is not EP-exclusive benefit.
- Most old ICNT1024/MissQ256/Lower256/Return384 results are zero or small; keep the negative results and avoid wide reruns.
- Stencil accepted WV4768893 versus S5242939 is1.0994x at original850; its fullF is4769712. Do not repeat this completed WV reference.

New G64 and scheduler points for FWT/GEMM are NOT_RUN. The short-family purpose is to test different reuse/traffic classes with known effective-capacity and headroom witnesses. The full table reports absolute EP and S baselines separately from the same-background ratio; ratio gains caused by S regression do not count as EP improvement.
