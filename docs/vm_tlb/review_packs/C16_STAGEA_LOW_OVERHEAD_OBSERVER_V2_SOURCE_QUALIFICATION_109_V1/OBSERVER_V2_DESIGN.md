# Observer V2 design

## Measurement separation

V2 defines two different artifacts and does not substitute one for the other:

- The instrumentation-OFF run is the authoritative native request-wall timing.
- The instrumentation-ON/NSYS run supplies semantic chronology and CUDA
  kernel/NVTX correlation. Its wall time is only a neutrality check and is not
  an authoritative scientific timing.

Only one start/stop CUDA Event pair surrounds the complete request. No semantic
module hook creates or records a CUDA Event.

## Hook contract

The forward pre-hook assigns a monotonically increasing ordinal, obtains the
first tensor input shape, creates the stable label
`C16_STAGEA_<ordinal>_<module>`, and pushes that NVTX range. The forward
post-hook pops the range and records the ordinal, module name, input shape, and
first tensor output shape in host metadata. Hook removal fails if any range is
unclosed.

The module selector is unchanged from V1:

- all selected self-attention modules;
- Qwen `gate_up_proj`, `act_fn`, and `down_proj` modules;
- OLMoE `gate` and `experts` modules (retained in source but not authorized in
  the first V2 GPU canary).

## Diagnostic-question coverage

- **DQ1, operator/phase wall union:** compute the union of CUDA activity
  correlated with the repeated module-level NVTX ranges in the NSYS timeline.
  Do not sum overlapping ranges and do not use removed per-module Event times.
- **DQ3, slow-window kernel correlation:** use the stable ordinal/module labels
  and the CUDA API/kernel correlation in the same NSYS capture to identify the
  kernels issued by slow semantic windows.
- **DQ4a, producer-consumer chronology:** use the ordered, nested NVTX ranges
  and matching host ordinal/shape receipt to establish launch chronology and
  shape identity.

This granularity is intentionally finer than a single request range. It retains
the chronology needed by DQ1/DQ3/DQ4a without placing GPU timestamp operations
on every module occurrence.

## Neutrality and correctness gate

The pre-registered V1 rule remains exact:

`abs(median_on - median_off) <= max(5 ms, 10% * median_off)`

The canary must also show exact generated tokens, exact routing where the target
has routing, exact semantic shapes/order, and exact kernel inventory. The first
canary contains only QWEN_AWQ, so routing is not applicable. Failure of any
required check leaves the observer non-neutral; it does not trigger a threshold
change.

## Source boundaries

The V2 patch changes only `HookSession` bookkeeping and its receipt. Static
qualification requires all of the following:

- zero `torch.cuda.Event` construction in `HookSession`;
- exactly two `torch.cuda.Event` constructions in request-level `generate`;
- NVTX push/pop and semantic ordinal/input/output-shape receipt preserved;
- semantic module selector and target configuration unchanged;
- profiler-based kernel inventory and correctness paths unchanged;
- Python compilation and exact clean-base patch replay pass.

Source qualification cannot prove runtime neutrality. It only establishes that
the bounded QWEN_AWQ V2 canary is technically well-formed for project review.

## Claim boundary

This is instrumentation qualification, not Tier0 science. It authorizes no GPU
run by itself and produces no operator-performance, model-performance, or
headroom claim. NCU, NVBit, SASS capture, OLMoE execution, and all scientific
Tier0 measurements remain outside the draft.
