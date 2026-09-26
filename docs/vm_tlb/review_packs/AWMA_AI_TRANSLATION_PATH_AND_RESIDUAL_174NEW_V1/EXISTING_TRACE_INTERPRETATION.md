# Existing-trace interpretation

The conservative B1 path model reuses accepted 0/80 reference runs because
`max(10-cycle L1 TLB - 32-cycle L1D, 0) = 0`. This is a timing composition,
not a claim of zero-cost translation.

Relative to B0, B1 changes cycles by +7.037% on T0, -1.983% on T1, +12.822%
on T2, and +1.269% on A2. Thus much of the prior 0/80 response is attributable
to the sequential access-path model. T1's regression also shows the response is
not a removable additive “translation runtime fraction.”

B1 preserves every translation and data request contract, but changed timing
can perturb cache/TLB interleaving; both arms' service and L1D outcomes are
reported rather than assumed equal. `vm_translation_stall_cycles` is a retry/
stall-event count, not kernel cycles that can be added.

B2 is not run. A valid virtual-L1 filter requires virtual cache tags,
permissions, synonyms, coherence, and shootdown semantics absent from the
current physical-cache interface. Treating an eventual L1 hit as known before
translation would be future information.

Existing traces therefore establish access-path-model sensitivity, not a new
program-intrinsic MMU bottleneck. Native-atlas evidence is still required to
test whether new AI dimensions leave a residual after the realistic path
diagnostic.
