# Single RTC reference-semantic repair

Pinned LeRobot RTC source computes `v_t` before `x_t.requires_grad_(True)`. Under the exact wrapper and outer `torch.no_grad()` inference context, `v(x)=2x` gave identity-only VJP in all 9 CPU cases (three shapes × three nondegenerate times); it gave the full `(1-2t)*error` VJP in 0/9. This is `UPSTREAM_RTC_VJP_SEMANTIC_GAP_OBSERVED`.

The sole reference repair moves `x_t.requires_grad_(True)` immediately before `original_denoise_step_partial(x_t)` inside the existing `torch.enable_grad()` block. No formula, weights, schedule, denoising step, or model source changes. The repaired exact module passed the full analytic VJP in 9/9 and identity-only in 0/9. Its SHA and patch hash are in `SOURCE_IDENTITY.json`; the literal patch is `util/vm_tlb/awma/vla_rtc_vjp_boundary/REFERENCE_REPAIR.diff`. Repaired-vs-upstream timing is never treated as speedup.

The first real-model observation hook was placed on an expert layer wrapper that this source never invokes; that instrumentation attempt failed only its hook assertion. Moving the hook to the actual expert q_proj submodule left model semantics unchanged. The successful real-model canary observed 10 VJPs, 10 action-output backward hooks and 10 expert-q_proj backward hooks, frozen parameter gradients, and detached prefix outputs. This was a probe correction, not a second reference repair.
