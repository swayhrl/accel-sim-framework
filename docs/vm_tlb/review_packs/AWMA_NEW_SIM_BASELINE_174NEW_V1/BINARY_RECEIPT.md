# Binary receipt

Qualified binary SHA256:
`34deedd99e85e52fb309852de2ecc5fecd9471436a33a5e77d40bc038a2c31c4`.

With its private runtime library path, this binary parsed the F0 VM
configuration and consumed both hash-closed recovered compute lists. Prefill
and Decode reached `gpu_sim_cycle = 10000`, emitted nonzero VM/TLB/PTW/cache
telemetry and exited through the simulator maximum-cycle boundary. These are
`FIXED_WINDOW_PARTIAL` runs, not full-ROI completions.
