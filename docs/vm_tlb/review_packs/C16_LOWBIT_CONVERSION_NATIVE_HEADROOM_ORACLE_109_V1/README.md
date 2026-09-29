# C16 Low-Bit Conversion Native Headroom Oracle — Lane 7

Task: `C16_LOWBIT_CONVERSION_NATIVE_HEADROOM_ORACLE_109_V1`

One discovery target is frozen at `M=256,K=4096,N=49152,split=1,GROUP_M16`.
One validation target is frozen at `M=256,K=3072,N=49152,split=1,GROUP_M16`
but may run only when discovery gives an isolated oracle median speedup of at
least 1.10 with baseline/oracle CV at most 5%.

Conditions:

- `STRONG_W4_BASELINE`: semantic-compatible accepted grouped W4 path.
- `ORACLE_FREE_TRANSFORM`: performance-only invalid-output diagnostic retaining
  compressed loads, shared-memory staging, MMA, and output stores.
- `PREDECODED_CORRECT_DIAGNOSTIC`: correct FP16 materialization outside timing
  plus the available dense `torch.mm` path.

Final decision: `NO_LOCAL_ORACLE_HEADROOM_STOP_VALIDATION`.

Discovery medians are 1.270784 ms (A), 1.538048 ms (B), and 1.162752 ms
(C).  The local oracle speedup is 0.8262x, so the frozen validation target was
not run.  Correct predecode is 1.0929x faster but expands the weight from
104,595,456 to 402,653,184 bytes and changes the kernel path.

The oracle is not an implementable mechanism or strict physical upper bound.
One initial runtime dependency canary was insufficiently sensitive and stopped
before timing; it is retained in the raw index.  A whole-tensor low-bit canary
then verified qweight, qzeros, and scales dependencies before the bounded
discovery measurement.
