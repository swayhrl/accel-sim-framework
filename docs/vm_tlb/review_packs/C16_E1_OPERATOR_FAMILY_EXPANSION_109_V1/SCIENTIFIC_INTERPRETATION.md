# C16 E1 operator-family expansion interpretation

Stage label: `OPERATOR_FAMILY_NOT_SUPPORTED`.

The runtime call-order authority closes 420 natural FFN invocations per full run in measured gate→up→down order. All fourteen preregistered conditions preserve tokens, all 84 FFN identities, exact qweight windows, and one fixed requested/actual set-aside.

Role-only persistence is highly asymmetric. UP28 retains strong direct up_proj saving, while GATE28 and DOWN28 show essentially no direct selected-family benefit. Protecting UP28 makes measured gate/down timing slower, and a large negative residual remains outside measured FFN accounting. Pairwise conditions do not remove that residual. Under GUD84, direct FFN saving is about 0.464 ms per stable step, but only about 0.009 ms appears in whole decode; median outside-FFN residual is -0.436 ms. This is reported only as a negative residual outside measured FFN accounting, not as proven cache collateral slowdown.

No predeclared condition reaches the 2% whole-decode gate or even a positive-beyond-dispersion subthreshold result. GUD84 has only one-third of selected modules MATERIAL_LOCAL, so FULLHINT is not triggered. Representative NCU reproduces up_proj GEMM duration/stall benefit, finds a smaller gate GEMM effect, and little down_proj change, while L2/DRAM-read counters remain nearly flat.

The evidence does not justify automatic bounded trace or simulator implementation from this producer. No simulator, NVBit, or trace work was run.
