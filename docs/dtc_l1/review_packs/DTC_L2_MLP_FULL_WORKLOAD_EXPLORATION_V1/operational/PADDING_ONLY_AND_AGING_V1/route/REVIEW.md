# Padding-only CLI route — independent qualification

**41 CPU checks PASS; 0 models, 0 signals, 0 production changes.** The candidate routes only explicit `experiment prepare/inspect/run-native E2-DTCL2MLP-*` calls containing exactly one `--padding-only-admission-v1` and one `--project DTC_L1` to:

`/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/padding_only_v1/padding_frontend.py`

`build_route.build(original_bytes, frontend_path)` permits the coordinator to choose a different absolute deployment path. Such a change needs a regenerated route/hash and fixture qualification.

## Preservation and fail-closed behavior

The original native entry is **4212 bytes**, SHA256 `79adadd961a1e3ef2593a39c5b8ff603c30dd9076329f8b5b988a1975a2718da`. All of those bytes remain the exact suffix of `native.candidate.sh`; the added prefix is1941 bytes. Candidate SHA256:

`d1e7c0c9345a48bc54a55b88149c345b349f8c8a457156964be919a4cdaacde5`

Every command without the padding opt-in follows the unchanged original body. Actual shell tests compared legacy argument vectors, selected targets, exported route flags, stdout/stderr and return codes for ordinary L2, HASH18, EP multiworkload/matched/capacity, fallback and quoted literal arguments. All matched exactly.

Explicit padding opt-in with a wrong area/cohort/operation/project, duplicate flags/project, unknown option, missing value or misspelled padding-version flag fails with HOLD. The prefix never silently forwards a malformed opt-in into the permissive old frontend.

The shell does **routing only**. ACTIVE operational metadata, registered allowed cohorts, source/policy/certificate/frontend/additional-strict/qualification/publication pins and unused scientific identity are B frontend/coordinator responsibilities. Missing/inactive metadata in the fixture private gate returned HOLD; that fixture is not evidence of a real central-registry qualification.

## Safe execution of fixtures

`N/bin/experiment` contains an absolute jump to production `N/bin/native`. It was read and hashed but **never executed**. The fixture uses its own independent experiment wrapper that points solely to an instrumented candidate.

Every execution target in both old and candidate fixture copies was replaced with a CPU-only argument sink. Even the `run-native` routing cases therefore execute no original frontend, launcher or model. `sh -n` passed for original, candidate, both instrumented versions and the independent wrapper.

The production native SHA was identical before/after. The builder and qualifier never write any production path.

## Existing strict/binding compatibility

The native and experiment CLI entries are absent from the current **21 source pins**. The frozen base `identity()` checks host, namespace, boot, device and filesystem; it does not hash the CLI. The unchanged L2 strict validator checks source/build/options/dispatch/observer bindings and raw natural completion, not the current CLI text.

A read-only full strict control on existing gaussian DH-E384 remained accepted at **740717 cycles**. No record was edited and no candidate was installed. This control supports the source-dependency assessment; it does not claim that an uninstalled route has been production-tested.

Main must recheck the current native SHA immediately before installation. If another lane prepends a route meanwhile, regenerate against those latest bytes and repeat the small shell checks; never overwrite another lane's entry changes.

Evidence: `SOURCE_EVIDENCE.json`, `ROUTE_MANIFEST.json`, `CPU_ROUTE_QUALIFICATION.json`. The separate padding resource algorithm and additional strict acceptance remain subject to their independent qualification. All pause/SIGSTOP guard candidates remain PRODUCTION_HOLD.
