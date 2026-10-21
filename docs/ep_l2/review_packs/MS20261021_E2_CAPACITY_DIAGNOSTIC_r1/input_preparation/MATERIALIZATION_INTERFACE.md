# Materialization draft for formal new-runtime inputs

`materialize.py` has not been run. It cannot execute without three real input documents and the explicit `--materialize-formal-release` flag. It only writes a previously absent child directory of `input_preparation/`; it never registers qualifications, mutates registry/CLIENT, acquires leases, launches a controller, builds a binary, or runs native/application tests. No placeholder producer files have been generated.

The owner supplies:

1. `--source-identity`: the formal source identity itself, or an object containing `source_identity`. It must contain real `core_source_commit`, `framework_source_commit`, `vendor_pybind11_commit` and `binary_sha256`; the main SHA must differ from main61.
2. `--capacity-manifest`: the actual frozen producer capacity manifest. The materializer hashes the entire file. Each independently E-qualified contract must name this exact hash.
3. `--qualifications`: a real E binding index with the fields below. Its schema is `E2_CAPACITY_MATERIALIZATION_INPUTS_V1`, status is `E_INDEPENDENT_QUALIFICATION_COMPLETE`, and authority is commit `49343880865edb22a17523790fc32dd55975966c`.

The E index contains `producer`, `binary`, `archive` and `workloads`. All content references are real absolute `path` plus exact `sha256`, checked by reading the file. `producer` contains the formal Git `commit`, a `release` reference, and a `remote_readback` reference. The release's current bytes must equal its exact committed Git blob; the remote readback must contain the same `remote_commit` and a nonempty `verified_paths`. `binary` and `archive` reference their separate production artifacts.

`workloads` has exactly the five approved workload names. Each entry contains `qualification` and `new_input_review` references. Each qualification must have the exact common new `source_identity`, both supported profiles `S` and `S_L2_DATA_FREE_LARGE_CAPACITY`, a new exact parser reference, all real production-driven PASS gate evidence, and the eight affected capacity gates required by the published `capacity_policy.qualification`. Its `capacity_diagnostic` contract must additionally contain:

- `capacity_manifest_sha256`, matching the supplied complete manifest;
- `producer_release_commit`, matching the formal producer;
- `archive_sha256`, matching the actual production archive;
- the policy-required authority, master option, common capacity vector and native geometry.

Every profile's exact `effective_options`, feature/ideal vectors and labels come from that new E qualification. `comparison_variable_options` must be exactly the one master switch. The prepared OFF/ON configs must match those whitelists byte-derived by the original option parser. If the actual A option spelling or effective config differs, the owner must first update and independently qualify the exact configuration; this script never silently adapts it.

Each `new_input_review` is an independent E/E2 PASS document naming the full new source identity, workload, exact trace-content identity, and `new_runtime_reader_semantics_independently_reviewed=true`. It must explicitly supply the new `input_scope_admission`, exact `auxiliary_assets`, `atomic_input_scope`, and any applicable `native_legacy_semantic_proof`. There is no fallback to the old main61 admission. For the existing unchanged-reader adapter, `input_scope_admission.retained_input_scope` must reference a newly hashed `UNCHANGED_COMPLETE_INPUT_PARSER_AND_CONTENT_SCOPE` report, bound to the new source identity, real equal source-tree objects, and passed new host-prefill/read-reference tests. The original atomic/native-legacy closure functions then validate the retained complete-content evidence through that new binding. A changed native reader requires owner review and a different concrete adapter; it is rejected by this draft.

The script independently hashes the complete current trace content once per workload, checks the original selection and full instruction count, validates original config/trace/atomic/native-byte closure, and computes `runtime_config_sha256` using the original ordered config manifests, auxiliary manifests and explicit environment. It computes the same comparison invariant as `runner.inspect`, excluding only the master option, and requires that invariant to be equal within each pair. Final run keys come from the original `run_key` function with actual new identities; any existing attempt with that key is rejected. It requires the original central amendment and exact policy matrix to be present and the charged count to remain 36 at first materialization.

The final naming is fixed:

| Item | Form |
| --- | --- |
| OFF condition | `V3_CAPACITY_<workload>_S_OFF` |
| ON condition | `V3_CAPACITY_<workload>_S_ON` |
| OFF profile | `S` |
| ON profile | `S_L2_DATA_FREE_LARGE_CAPACITY` |
| Budget bucket | `five_input_capacity_diagnostic_user_approved_20261021` |
| Comparison group | `CAPACITY_DIAGNOSTIC_<workload>` |
| Pair ID | `CAPACITY_DIAGNOSTIC_<workload>_OFF_ON_NEW_RUNTIME` |

The default output child is `input_preparation/materialized/`. It contains ten full specs, `INPUT_CONFIG_REVIEWS.json`, `QUEUE.json` and `PLAN.json`. The queue preserves the original dispatcher's `coordinator.AUTHORITY`, with the new approval recorded separately as `capacity_authority_commit`; changing the queue authority alone would violate the original controller's frozen entry contract.

`PLAN.json` provides the report interface requested by the root owner: top-level `source_identity`, `conditions` and `pairs`. Each condition contains `condition_id`, `profile`, `pair_id`, `qualification_id`, `run_key` and `spec` content reference. Each pair contains `pair_id`, `left_run_key` and `right_run_key`. All spec references point to their actual final generated locations. Owner E can publish these exact files and place a verified plan copy at the root pack for `report.py`; no materialization operation is a permission or resource lease to execute.

Per-endpoint result caps remain 384 MiB and timeout 10,800 seconds in this draft; the ten endpoints reserve at most 3.75 GiB plus 64 MiB collector/metadata planning allowance. Actual admission stays with the original controller and original current safety checks. This draft never schedules a retry, replacement workload, old-binary anchor, or extra application.
