# Scientific interpretation

Decision: `NO_LOCAL_ORACLE_HEADROOM_STOP_VALIDATION`.

The strong W4 baseline reproduced the accepted discovery output bitwise and ran
3.50% faster than its accepted historical median, within the preregistered 5%
calibration boundary.  Its median was 1.270784 ms, CV 4.12%, with bootstrap
median 95% interval [1.269248, 1.275376] ms.

The invalid-output oracle retained compressed qweight/qzeros/scales loads,
shared-memory traffic, all 16 HMMA instructions, all 32 global output stores,
and barriers.  It removed all 50 HADD2 and 50 HFMA2 conversion instructions.
Runtime canaries proved each compressed source affects the output.  Despite
that isolation, its median was 1.538048 ms, CV 2.99%, interval
[1.532928, 1.543680] ms.  Baseline/oracle local speedup was 0.8262x with
bootstrap 95% interval [0.8228, 0.8303]: no positive local conversion headroom.

This negative result does not prove dequantization is intrinsically beneficial.
It shows that, in this strong kernel, removing the half conversion sequence and
replacing it with a serialized compressed-load dependency does not expose a
faster local path.  Conversion may already be hidden by the surrounding load,
shared-memory, and MMA schedule; the oracle dependency codegen can also impose
its own scheduling cost.  It is neither an implementable mechanism nor a strict
physical upper bound.

The correct predecoded diagnostic matched baseline output bitwise.  Its dense
GEMM median was 1.162752 ms, CV 4.80%, interval [1.157120, 1.169264] ms.  The
1.0929x speedup interval was [1.0861, 1.0988], but the representation grew from
104,595,456 to 402,653,184 bytes (3.8496x), materialization was deliberately
outside timing, and the dense kernel differs.  This is modest diagnostic value,
not pure conversion time or a free upper bound.

Because the discovery oracle failed the frozen 1.10 gate, the K3072 validation
target remained frozen and unexecuted.  No parameter scan or follow-on positive
search was performed.
