# Claim boundaries

| Tempting claim | Admitted wording | Evidence / why bounded |
|---|---|---|
| CUDA persistence exposes NVIDIA's true replacement policy | Targeted CUDA L2 persistence restores tested local timing benefit | Persistence consumer `SCIENTIFIC_INTERPRETATION.md`; API behavior does not disclose hardware victim policy. |
| Aggregate self-attention slowdown is caused by one cache event | The aggregate native self-attention offset is measured; representative L0 D3 NCU does not reproduce it | Budget consumer `SCIENTIFIC_INTERPRETATION.md` and `FINAL_DECISION.json`; unique microarchitectural cause remains unestablished. |
| The oracle is a deployable qweight classifier | Exact software-region identity isolates a replacement opportunity | Oracle mechanism spec and implementation `FINAL_DECISION.json`; autonomous classification is future work. |
| Simulator cycles directly calibrate an earlier native timing run | Counterfactual direction and mechanism behavior are evaluated on an admitted bounded trace | Trace admission audit and B16 design. Tensor-byte identity to the early timing run is not established as the same input; absolute per-run cycle calibration is excluded. |
| Opcode coverage proves Ada timing fidelity | The admitted SASS bundle has parser execution compatibility under the qualified adapter | Namespace pack `SM89_TO_AMPERE_FULL_BUNDLE_OPCODE_AUDIT.json`; no complete Ada microarchitecture fidelity or cycle-perfect reproduction claim. |
| Negative residual proves cache collateral damage | Other top-level semantic work offsets local benefit in measured native timing | Cost/benefit independent decomposition; cause remains open. |
