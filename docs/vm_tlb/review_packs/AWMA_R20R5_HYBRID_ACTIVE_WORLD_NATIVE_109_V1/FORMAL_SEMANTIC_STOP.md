# Interrupted formal discovery: exact-niter hard gate

The exact source, input, threshold=304, worker=304 and B0/H1 captured graphs were fixed before timing. Three paired groups × four entries × two arms × (two warmups + five formal samples) were preregistered. Timing samples include complete solver graph wall/CUDA-event intervals; debug branch observer was OFF. Every formal sample is checked after the timed interval against the accepted source-semantic and effective-output contract.

The first 128 completed sample rows contain 38 warmups and 90 formal samples, all formal rows reported semantic PASS. The next attempted sample was group 2, t136, B0, formal repeat 0. Its recorded wall/CUDA-event intervals were 0.726818/0.719872 ms, but `check_output` found `solver_niter_exact=False` against the frozen t136 B0 authority. The same exception row reports `nefc_exact=True` and `source_stop_fail_count=0`. This is enough to fail the exact hard gate; source-stop truth alone cannot override outer-niter mismatch.

The failing process exited before persisting that output array or the full planned 168-row table. `DISCOVERY_TIMING_PARTIAL_SAMPLES.tsv` on node164 was reconstructed solely from the stdout JSON lines; the original stdout/stderr are kept with SHA hashes. It is **incomplete diagnostic data**, not a valid three-group performance result. The differing world and whether the cause is baseline arithmetic-order variation, graph-local state, or another factor cannot be determined without a new authorized study. No performance estimate from the partial rows is promoted to a scientific conclusion.

The mandatory “all 120 formal samples semantically qualify” gate failed. No further R20 candidate, timing restart, holdout or profiler action is permitted by this Goal.
