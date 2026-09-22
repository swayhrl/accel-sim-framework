# Candidate semantic recalibration options (not implemented)

1. Model L1-hit translation readiness with non-HOL downstream overlap; needs hardware/reference evidence for translation/data-pipeline overlap and carries trace/reproducibility risk.
2. Separate pipelined L1 lookup throughput from requester serialization; needs validated port/service semantics and may change all historic results.
3. Preserve zero-latency diagnostics but prevent same-cycle retry ordering from changing duplicate admissions; needs a formal replay/ordering contract.

No option is implemented. ChatGPT review is required before any model change.
