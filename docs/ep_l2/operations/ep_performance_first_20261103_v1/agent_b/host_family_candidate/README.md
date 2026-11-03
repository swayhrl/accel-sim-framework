# Six-cell pure Host DRAM family contract candidate

Status: PASS pure engineering contract, not complete Host/native/application qualification. The old runtime, native entry, accepted Core/ELF, budgets and registries were not modified.

`family_contract.py` is standalone and pure. Every API defaults to rejection (`engineering_enabled=False`). An explicit `engineering_enabled=True` permits only this bounded offline check; every return states scientific launch permission false. It does not execute processes or change scientific state.

Allowed cells are embedded in source, with immutable SHA-bound exact reference specs: FWT S/WV_ZERO_RO1020, GEMM S/WV_ZERO_RO1020, Vector4M S/F1275. Full Source78Source5, input binding/member metadata, binary/library paths, geometry, observer, typed M/T, formal switches, completion expectations, SourceKEEP and limits must match the corresponding reference. Exactly282 string options must equal that reference except its clock string. For VectorF, the exact qualified RO certificate and small manifest/ranges hashes are checked; disabledRO modes cannot inherit a certificate. No large trace body or ELF hash is recomputed.

`validate_pair` requires exact same-workload S/EP arms at the same clock/profile/input. Only the formal five mechanism switches and RO-binding options may differ; other282-option values must be identical. `validate_packet` requires exactly all six distinct cells. Positive individual points alone cannot satisfy the fair-pair requirement.

Run bounded CPU checks:

    python3 -B test_family_contract.py

Actual result:50/50 PASS, including six points, three S/EP pairs and the complete packet. Negative controls cover defaultOFF, invalid cell/profile/cohort, Source/ELF/input/clock changes, P2/D1024/MissQ/Tag/latency/background drift, observer changes, missing/mismatchedRO, mismatched pairs, incomplete/duplicate/extra packet, and immutable-reference absence. No GPU/model was invoked. The earlier oldHost-rejects-newprofile result is separate; this new checker actually accepts the precise intended cells and rejects unauthorized variants.

Integration boundary: `candidates/*.json` are engineer-only complete objects, not frozen runnable specs. Their original ordered-config references remain immutable anchors; no frequency overlay was installed. Main must generate and pin new configuration overlays, verify actual effective282 echo, bind the new family checker/profile and Source5 in HostQ/native contracts, establish current scoped user authorization/budget/resource admission, and retain full acceptance/archive/drain checks. This contract cannot replace those steps. Its anchor-only ordered_config rule may need a controlled Main integration adapter which compares effective282 plus pinned overlay order; do not remove the protection without that replacement.

UnchangedSource78 / existing observers do not create a new observer or inherit newSource eligibility. No performance, appNI or full constructor/drain pass is asserted by these50 pureHost tests.
