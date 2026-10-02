# AWMA R21A OEQ graph-readiness Native screen

Trained model: `nequip.net:mir-group/NequIP-OAM-S:0.1`, package SHA256 `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`. Real discovery geometry: pinned `sitraj.xyz` frame 55 of 110; the file is a collection of real periodic Si frames and is not interpreted as a time sequence.

The natural graph has 1,394 directed periodic edges and is receiver-major, but not sender-monotonic within receiver rows. The natural-order transpose-only deterministic probe failed forces; NequIP's source-backed composite receiver/sender ordering and one sender transpose permutation were needed. That prepared representation is shared across both interaction layers.

A0 and Dready use the same official NequIP AOTInductor ASE CUDA path, float32 and TF32 OFF. A0 and Dready each passed five energy/force evaluations at `atol=rtol=5e-5`.

Dready did not pass the MATERIAL timing gate: median wall improvement `4.7047%`, below 5%, and only one of three groups passed 3×MAD. Final status is `R21A_RESULT_MIXED_NEEDS_REVIEW`; Donline and holdouts are NOT_RUN. This supports only a bounded Native diagnostic and no deployment, rebuild-frequency, temporal-MD, hardware, or cross-model claim.
