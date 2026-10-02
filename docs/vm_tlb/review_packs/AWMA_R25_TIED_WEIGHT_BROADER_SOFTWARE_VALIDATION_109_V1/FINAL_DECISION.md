# R25 final decision

`R25_TILED_CAPACITY_TIME_TRADEOFF`

Both D0 and the independent H0 passed one-step and four-step trajectory qualification. C1 has one full classifier/total gradient and no dense lookup gradient; S2 has no full VxH gradient in formal execution.

- D0: S2 vs C1 saves 535.777 MiB (19.220%) and is `BENEFIT` in all three TARGET_REGION groups.
- H0: S2 vs C1 saves 1350.030 MiB (22.944%), but is `REGRESSION` in all three TARGET_REGION groups; the overall median regression is 0.130%.

Thus capacity generalizes across model/input lineage, while timing does not remain neutral/favorable under the preregistered classifier. This is a software/dataflow capacity-time tradeoff, not a hardware, convergence, full-training, or general-LLM-speedup result. NSYS was skipped because direct buffer identity and allocator accounting closed the causal question.
