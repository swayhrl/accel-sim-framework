# Known limitations

- `BASE_CONCURRENCY_MODEL_RESIDUAL`: even V1 0/80 does not reproduce Native A32_W8/A32 behavior. Do not tune the platform or V1 to chase it.
- A1_CONTROL is one 128B line at trace level but four 32B sector accessq entries under the simulator coalescing contract.
- RTX4080 platform scope is `QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`, not universal cycle-accurate RTX4080 fidelity.
- Matched H_STREAM/H_COMPUTE held-outs are small and launch-dominated; they do not independently establish full streaming/compute fidelity.
- 10/80 is a model-relative research overlay, not a hardware TLB latency claim.
- T0/T1 0/80 retain a scoped V1 prelaunch-ordering residual: V1 launches translations before head consumption and leaves READY results unapplied by design. This increases lookup activity without changing coverage or side effects.
