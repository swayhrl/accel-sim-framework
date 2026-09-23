# Scientific interpretation

Independent raw consumption closes successfully against producer `4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`.

- CUDA persistence policy is qualified. Exact qweight regions are contiguous 33,947,648-byte intervals. Full-qweight request 33,947,648 B queried back as 37,748,736 B; this is recorded as runtime-observed rounding, not a general alignment theorem.
- Isolated positive control: timing 35.9114% lower and DRAM 61.4780% lower.
- All four natural primary points have material, target-specific timing benefit. No primary point passes the frozen DRAM gate of at least 20% and at least 4 MiB. L0 up D3 DRAM benefit is 19.510142%; it is not rounded to 20%.
- Budget sweep: 16 MiB is the first tested timing-material budget. No tested budget passes the DRAM materiality gate. This is not an exact threshold.
- Producer scoped state: `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`.
- Frozen strict consumer state: `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`.

The state divergence is methodological operationalization, not a raw-evidence mismatch. Producer requirement content is descriptively evidence-backed, but that does not make the strict preregistered READY gate pass. Project-level authorization remains `REVIEW_REQUIRED`.

No GPU, NVBit, full trace, mechanism implementation, or mechanism simulation was used or authorized by this consumer.
