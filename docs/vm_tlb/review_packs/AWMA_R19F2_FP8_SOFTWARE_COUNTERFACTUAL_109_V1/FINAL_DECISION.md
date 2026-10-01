# Final R19F2 decision

`R19F2_FUSED_SOFTWARE_SUFFICIENT`

Stage A established an exact natural Qwen layer0 gate/up shared-FP8-input counterfactual. A single TE quantization shared across sibling consumers removed some duplicated readiness work but left a stable `17.29%` complete-MLP S1→D0 gap and recovered only `29.21%` of the B0→D0 ideal headroom. This correctly triggered Stage B; a projection-only result was not promoted to an MLP claim.

Stage B source audit found no direct standalone exact single-launch per-tensor E4M3 current-scaling path in the pinned TE v2.19 or the separately inspected current-main source. Exactly one minimal cooperative CUDA software diagnostic was implemented. On the *same real X*, it produces TE-identical FP8 bytes and inverse-scale bytes, unchanged gate/up TE GEMMs, unchanged cached weights, and bitwise-identical gate/up/downstream MLP outputs. Its formal complete-MLP S2−D0 residual was `4.04%`, with nonuniform paired-group sign and no >3×MAD margin; S2 recovered `84.09%` of the Stage-B S1→D0 ideal headroom. The user-predeclared software-sufficiency gate therefore closes the line.

The Stage-B extension is an opt-in bounded diagnostic with preallocated buffers, not a claim that stock TE v2.19 ships this fusion or that a complete Qwen inference request improves by these percentages. The old R19 V1 BF16-versus-FP8 numeric failure remains unchanged; R19F2 compares equal FP8 representations and consumers. The sole new NSYS capture proved Stage-A exact native SM89 E4M3 gate/up GEMMs and 2/1/0 quantizer-call strata; no NCU, NVBit, SASS inspection, Accel-Sim, node174 computation, hardware mechanism, second model, second shape, second recipe or FP4 extrapolation followed.

Scientific STOP: no `READY_FOR_ARCHITECTURE_REVIEW` label from this Goal. Any production integration or model-level quality/latency study requires separate authorization.
