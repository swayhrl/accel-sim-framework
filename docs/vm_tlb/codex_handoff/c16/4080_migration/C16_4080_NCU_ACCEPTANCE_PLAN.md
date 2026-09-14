# C16 RTX4080 NCU acceptance plan

NCU is a required first-class acceptance capability. The historical RTX3090 `ERR_NVGPUCTRPERM` is a negative control only; it neither predicts 4080 permission nor authorizes skipping NCU.

All raw `.ncu-rep` files remain outside Git. Git contains only receipts, manifests, SHA256 values, immutable metric/command definitions, and derived analysis. Formal NCU and formal NVBit model captures are separate processes and separate windows; loading both in one model run is forbidden.

| Gate | Required action | Pass evidence | Stop condition |
| --- | --- | --- | --- |
| N0 ordinary-user permission | As the research UID, read loaded profiling state and NCU version; audit uid/groups/capabilities | Unrestricted profiler state after approved admin config; non-root; no sudo/docker/SYS_ADMIN | Unknown/restricted state or privilege violation |
| N1 tiny CUDA counter canary | One bounded, non-model CUDA canary under NCU using a reviewed compact metric file | `.ncu-rep` exists, report opens/exports, metric is present, process is research UID | `ERR_NVGPUCTRPERM`, no report, unexpected target, or privilege workaround |
| N2 immutable NCU version/metric freeze | Hash NCU version output, compact metric list, canary command, report/export, image digest and UUID mapping | Single frozen metric identity and SHA manifest | Metric/version/image/UUID drift |
| N3 frozen Llama native baseline | Run the Recovery-V2-S5 Llama contract without NCU or NVBit; bind actual 4080 runtime/model/input/checksum | Native receipt and checksum; no profiler injection | CPU fallback, model/revision/backend/dtype/offload drift |
| N4 4080 kernel census | Use a separately authorized, lightweight census to map the local 4080 code object and candidate kernel identity | Hash-closed census/catalog and exact target binding | Reuse of RTX3090 kernel/static identifiers or ambiguous target |
| N5 bounded Llama NCU capture | Run exactly the N2 metric set against one N4-bound target/window, with NCU only | `.ncu-rep`, command receipt, target identity, bounded wall time, clean process state | NVBit co-load, target substitution, unbounded replay, or failed cleanup |
| N6 report/export/SHA closure | Hash remote/local `.ncu-rep` and permitted export, validate report-to-command/target identity, retain manifest | Remote/local size+SHA equality; raw kept outside Git | Missing artifact, mismatch, or non-reproducible export |

## N0 and N1 rules

N0 does not profile a kernel. It is complete only after the approved modprobe change is visibly loaded and the research UID's no-sudo/no-Docker/no-SYS_ADMIN posture is recorded. N1 is a single small CUDA counter test, not a model result and not a metric fishing exercise. If N1 fails for permission, record the exact error and stop; do not run as root or modify group/capability policy.

## N2–N6 provenance contract

Freeze NCU executable/version, image digest, GPU UUID mapping, driver, CUDA/nvdisasm, compact metric file SHA256, command argv, canary binary SHA256, and output/export SHA256 before N3. The 4080 requires a new native baseline and a new kernel census because binary code identity may differ. The Recovery-V2 S5 result remains the last positive NVBit model reference; Recovery-V3 zero-address/predicate-off results remain diagnostic negative controls only.

Never publish an NCU counter result without its N6 closure. Never use NCU timing as native baseline timing; N3 is the unprofiled timing/reference lane.
