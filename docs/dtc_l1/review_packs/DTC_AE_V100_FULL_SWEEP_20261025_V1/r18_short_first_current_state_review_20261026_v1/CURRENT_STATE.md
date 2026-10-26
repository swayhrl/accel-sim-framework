# Latest actual status and retained qualification snapshot

**R18 is now actually active.** Read [ACTIVATION_STATUS.md](ACTIVATION_STATUS.md)
for the timestamped takeover and post-activation facts (CST09:57:16). The
pre-activation source/facts snapshot preserved below was correct at its earlier
cutoff; its R17-active/R18-not-yet-active wording is historical, not the latest
controller state. No original cutoff facts or qualification bytes were edited.

Latest ordinary accounting:288 =232 strictPASS +17 native negatives +3 receipt
gaps +19live +17not-started. Seventeen not-started means13admitted plus Cutcp4.
The20negative/gap cases include the new histoDH abort, not a PASS. Total live20
means19original plus1late validation. The three-week ETA remains an extrapolation.

---

## Original pre-activation review snapshot

# Current state at the R18 publication snapshot

**Actual controller: R17. R18: qualified, not activated in this snapshot.**
Root plans a separate activation-status commit only after verified publication
and real takeover. Read any later supplement with its own timestamp; this
original snapshot remains immutable.

Scientific question: can AE benefits survive matched traditional-cache-hash
controls? CM/CH/DM/DH are retained exactly as the original frozen fields in
scientific_question/FOUR_ARM_GOLDEN_TEMPLATES.json, with no guessed labels.
This package presents simulation/validation evidence, not an AE-benefit verdict.

The ordinary sweep concerns complete declared captured inputs, not proven
original native numerical results. Existing raw/SHA/population evidence covers
that trace domain only. Fraction/trim exclusions remain excluded. Correctness
validation on repaired sources is not merged into original performance data.
Nineteen original negative/receipt-gap cases remain unaccepted/preserved.
Cutcp4 and final-consumer closure are open. No complete original-matrix or paper
promotion is claimed. The last confirmed English master remainsv0.23.

Old R1 is independently CLOSED:23 archived/restored, effective21 correctness
PASS and two old native failures. Ten canonical sentinel ENGINEERING results
are deliberately preserved as history and independently closed by V2; they do
not mean ten unfinished strict reviews or permit rewriting legacy evidence.

The five actually consumed lava/late launches retain their original R16 launch
identity. The previous R17-specific operational-binding branch is supported by
explicit synthetic CPU tests; it is not represented as an observed real R17
scientific launch. The R18 bridge has separate actual-parent identity and keeps
the frozen R16 scientific engine/spec/plan/binary/input lineage visible.

The ETA of about three weeks is a planning extrapolation from observed windows,
not a completion promise. Short-first priority and remaining long jobs can change
throughput; different config/build estimates are heuristics. Exact per-point
window facts and open items are retained below and in STATE_FACTS_V1.json.

## Frozen quantitative and provenance facts

The following is copied directly from the independently collected facts JSON,
without live-registry normalization or acceptance reclassification.

The facts were captured at 2026-10-26T09:47:47.982044+08:00, before the final R18 qualification was written. Thus candidate_R18.qualification_exists=false is correct historical cutoff evidence. The later final qualification included here is PASS (SHA 72f111e38b0d000f29d223600a9b22333dc1df71d23b9f3848bf12111e8a2270); it establishes qualified-not-activated status without editing that older snapshot.

### observed_utc

```json
"2026-10-26T01:47:47.982044+00:00"
```

### actual_controller

```json
{
  "revision": "R17",
  "lease": {
    "pid": 1362882,
    "start_ticks": 972720947,
    "fd": 4,
    "request": "DTC_AE_V100_FULL_SWEEP_20261025_V1",
    "additional_requests": [
      "DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1",
      "DTC_AE_LAVAMEM_REPAIR_20261026_V2",
      "DTC_AE_LATE_FAILURE_REPAIR_20261026_V1"
    ],
    "controller_sha256": "62993baf0d7e1a21de76628a1219287206229fe8c8e67123773396886977eea2",
    "scope": "Real R17 continuation; original40/lava2/late4 existing budgets only;old23 independent metadata;no spent retries",
    "operational_parent_bridge_manifest_sha256": "749bb63c784fb60ca5177531cde71b4d01e0778438c7700e9870560e12fd4be7"
  },
  "lease_process": {
    "pid": 1362882,
    "start_ticks": 972720947,
    "state": "S",
    "same_generation": true,
    "alive": true
  },
  "cmdline": "/usr/bin/python3 -B /root/data/dtc_failure_repair_20261025_v1/ops/revision17/sweep_controller.py ",
  "actual_source_path": "/root/data/dtc_failure_repair_20261025_v1/ops/revision17/sweep_controller.py",
  "actual_source_sha256": "62993baf0d7e1a21de76628a1219287206229fe8c8e67123773396886977eea2",
  "qualification_FD_target": "/root/data/ep_l2_dtc_l1_native_v2/control/qualification_ledger/NATIVE_QUALIFICATION.lock",
  "qualification_FLOCK_observed": true,
  "registry_orchestrators_match_actual_R17": true
}
```

### candidate_R18

```json
{
  "active": false,
  "CONTROLLER_START_R18_exists": false,
  "qualification_path": "/root/data/dtc_failure_repair_20261025_v1/ops/R18_ZERO_MODEL_QUALIFICATION_V1.json",
  "qualification_exists": false,
  "qualification_status": null,
  "qualification_sha256": null,
  "publication_readback_path": "/root/data/dtc_failure_repair_20261025_v1/ops/R18_PUBLICATION_READBACK_V1.json",
  "publication_readback_exists": false,
  "statement": "Prepared/qualified or publication in progress only; no actual R18 dispatch or lease takeover at this cutoff."
}
```

### actual_original

```json
{
  "normal_full_input_vectors": 72,
  "cells_per_input": 4,
  "normal_scientific_matrix_cells": 288,
  "registered_admitted_vectors": 71,
  "registered_admitted_cells": 284,
  "registry_budget": 356,
  "historical_HOLD_cells_outside_normal288": 68,
  "registry_remaining": 91,
  "registry_state": "RUNNING",
  "consumed": 265,
  "counts": {
    "PASS": 231,
    "MISSING_OBSERVER_RECEIPT_GONE_UNACCEPTED": 3,
    "NATIVE_FAILURE_UNACCEPTED": 16,
    "LIVE": 15
  },
  "PASS_count": 231,
  "native_failure_unaccepted_count": 16,
  "observer_receipt_hole_unaccepted_count": 3,
  "known_nonpass_closed_or_hole_total": 19,
  "live_count": 15,
  "not_started_normal_total": 23,
  "not_started_admitted": 19,
  "not_yet_admitted_Cutcp_cells": 4,
  "accounting_identity": "normal288 = PASS + native failures + missing observer receipts + live + other actual pending postINTENT states + unstarted normal; budget356 additionally retains68 historical HOLD slots.",
  "normal_input_qualification_scope": "Ordinary complete trace-input vectors with body SHA/basic-format/declared geometry evidence; this is not full native CUDA numerical-result validation.",
  "pending_admitted": [
    {
      "cohort": "E2-AEV100-09f94fcc7494a03b-CH",
      "program": "hybridsort",
      "arm": "CH",
      "expected": {
        "CTA": 115324,
        "instructions": 6276086260,
        "kernels": 68
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-0e62c67daa020853-CH",
      "program": "srad_v1",
      "arm": "CH",
      "expected": {
        "CTA": 181000,
        "instructions": 10136693400,
        "kernels": 502
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-0e62c67daa020853-CM",
      "program": "srad_v1",
      "arm": "CM",
      "expected": {
        "CTA": 181000,
        "instructions": 10136693400,
        "kernels": 502
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-0e62c67daa020853-DH",
      "program": "srad_v1",
      "arm": "DH",
      "expected": {
        "CTA": 181000,
        "instructions": 10136693400,
        "kernels": 502
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-1213f9ab49665a65-CM",
      "program": "kmeans",
      "arm": "CM",
      "expected": {
        "CTA": 9747,
        "instructions": 2165609728,
        "kernels": 3
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-1213f9ab49665a65-DH",
      "program": "kmeans",
      "arm": "DH",
      "expected": {
        "CTA": 9747,
        "instructions": 2165609728,
        "kernels": 3
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-1213f9ab49665a65-DM",
      "program": "kmeans",
      "arm": "DM",
      "expected": {
        "CTA": 9747,
        "instructions": 2165609728,
        "kernels": 3
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-2c506bf13c81ff5d-DH",
      "program": "histo",
      "arm": "DH",
      "expected": {
        "CTA": 4260,
        "instructions": 2196264084,
        "kernels": 80
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-6df3a84b612086e8-CH",
      "program": "scan",
      "arm": "CH",
      "expected": {
        "CTA": 166608,
        "instructions": 1963460720,
        "kernels": 33
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-6df3a84b612086e8-CM",
      "program": "scan",
      "arm": "CM",
      "expected": {
        "CTA": 166608,
        "instructions": 1963460720,
        "kernels": 33
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-6df3a84b612086e8-DH",
      "program": "scan",
      "arm": "DH",
      "expected": {
        "CTA": 166608,
        "instructions": 1963460720,
        "kernels": 33
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-6df3a84b612086e8-DM",
      "program": "scan",
      "arm": "DM",
      "expected": {
        "CTA": 166608,
        "instructions": 1963460720,
        "kernels": 33
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-977a2f7007cb1f96-CM",
      "program": "3MM",
      "arm": "CM",
      "expected": {
        "CTA": 3072,
        "instructions": 1813512192,
        "kernels": 3
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-977a2f7007cb1f96-DM",
      "program": "3MM",
      "arm": "DM",
      "expected": {
        "CTA": 3072,
        "instructions": 1813512192,
        "kernels": 3
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-CH",
      "program": "SYRK",
      "arm": "CH",
      "expected": {
        "CTA": 4096,
        "instructions": 5626658816,
        "kernels": 1
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-c885293ad99e21ee-CM",
      "program": "stencil",
      "arm": "CM",
      "expected": {
        "CTA": 6400,
        "instructions": 2193446000,
        "kernels": 100
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-c885293ad99e21ee-DH",
      "program": "stencil",
      "arm": "DH",
      "expected": {
        "CTA": 6400,
        "instructions": 2193446000,
        "kernels": 100
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-ddb6806316876a85-DM",
      "program": "lavamd",
      "arm": "DM",
      "expected": {
        "CTA": 1000,
        "instructions": 10396775488,
        "kernels": 1
      },
      "admitted": true,
      "already_started": false
    },
    {
      "cohort": "E2-AEV100-ffc8a89493c8a211-DH",
      "program": "sgemm",
      "arm": "DH",
      "expected": {
        "CTA": 528,
        "instructions": 1658916864,
        "kernels": 1
      },
      "admitted": true,
      "already_started": false
    }
  ],
  "not_admitted_Cutcp": [
    "E2-AEV100-af7320f9d9dc6629-DM",
    "E2-AEV100-af7320f9d9dc6629-DH",
    "E2-AEV100-af7320f9d9dc6629-CM",
    "E2-AEV100-af7320f9d9dc6629-CH"
  ],
  "native_failures": [
    {
      "cohort": "E2-AEV100-09f94fcc7494a03b-DH",
      "uuid": "504a2712-5af5-4ffc-8239-dc49487959b7",
      "program": "hybridsort",
      "arm": "DH",
      "input_digest": "09f94fcc7494a03b160b40b705cbc7ff5f41e88e8ee417d187e5c7fbcac82123",
      "model": {
        "pid": 1268965,
        "requested_start_ticks": 969051670,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-09f94fcc7494a03b-DH.RESULT.json",
      "launcher": {
        "pid": 1268960,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 115324,
        "instructions": 6276086260,
        "kernels": 68
      },
      "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
      "launcher_wait_returncode": 1,
      "DONE_sha256": "5a710ab8a51f5382215d5af6e49135667741af3875576b911d34dedc7236ce14",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-09f94fcc7494a03b-DM",
      "uuid": "8ee5f9bf-e22c-4659-9eec-b79ec64247c7",
      "program": "hybridsort",
      "arm": "DM",
      "input_digest": "09f94fcc7494a03b160b40b705cbc7ff5f41e88e8ee417d187e5c7fbcac82123",
      "model": {
        "pid": 1247221,
        "requested_start_ticks": 968704958,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-09f94fcc7494a03b-DM.RESULT.json",
      "launcher": {
        "pid": 1247216,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 115324,
        "instructions": 6276086260,
        "kernels": 68
      },
      "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
      "launcher_wait_returncode": 1,
      "DONE_sha256": "0bd0a87589346f48ae357f27704f617f9cd60376eece262d9e5c4142663a9390",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-1df9d5479504d9c7-DH",
      "uuid": "a6161cff-a0fe-4f2d-b489-8644dcb61c89",
      "program": "bfs",
      "arm": "DH",
      "input_digest": "1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0",
      "model": {
        "pid": 1182515,
        "requested_start_ticks": 965569887,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-1df9d5479504d9c7-DH.RESULT.json",
      "launcher": {
        "pid": 1182510,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 76,
        "instructions": 121542388,
        "kernels": 11
      },
      "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
      "launcher_wait_returncode": 1,
      "DONE_sha256": "b07e1cd8d0ddd36e73571ac0dec01318d5690c313df59da347ef356407810ae1",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-1df9d5479504d9c7-DM",
      "uuid": "5d58a06a-8465-4dcf-bf31-391b5a6c4737",
      "program": "bfs",
      "arm": "DM",
      "input_digest": "1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0",
      "model": {
        "pid": 1073182,
        "requested_start_ticks": 962320373,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-1df9d5479504d9c7-DM.RESULT.json",
      "launcher": {
        "pid": 1073177,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 76,
        "instructions": 121542388,
        "kernels": 11
      },
      "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
      "launcher_wait_returncode": 1,
      "DONE_sha256": "712ee6b205e41893b86144f1978eee9c93d2d7af4ab39dcfdbbb1e1ea575ab52",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-2b93f70cd0666c51-CM",
      "uuid": "0a6cce7f-bb75-4fd6-a545-014d39ef8de0",
      "program": "scalarProd",
      "arm": "CM",
      "input_digest": "2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954",
      "model": {
        "pid": 1287771,
        "requested_start_ticks": 969727186,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-2b93f70cd0666c51-CM.RESULT.json",
      "launcher": {
        "pid": 1287766,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 128,
        "instructions": 730610912,
        "kernels": 1
      },
      "recorded_stop_reason": "DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "6acd0df19497a071fff0b513db30a3879c65cf7886c0cb0f9663b110656cff3e",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-2b93f70cd0666c51-DH",
      "uuid": "5fb1dece-aab7-459e-8dab-c53425d18972",
      "program": "scalarProd",
      "arm": "DH",
      "input_digest": "2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954",
      "model": {
        "pid": 1230628,
        "requested_start_ticks": 968058243,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-2b93f70cd0666c51-DH.RESULT.json",
      "launcher": {
        "pid": 1230623,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 128,
        "instructions": 730610912,
        "kernels": 1
      },
      "recorded_stop_reason": "DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "0821bf89b48e554537b5cb2d975b89726fded75f0e86e80e85b1c94fd5ed21f3",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-2c506bf13c81ff5d-DM",
      "uuid": "221010cd-8185-4a85-a380-9eaecff8de8b",
      "program": "histo",
      "arm": "DM",
      "input_digest": "2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64",
      "model": {
        "pid": 1269919,
        "requested_start_ticks": 969086764,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-2c506bf13c81ff5d-DM.RESULT.json",
      "launcher": {
        "pid": 1269914,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 4260,
        "instructions": 2196264084,
        "kernels": 80
      },
      "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
      "launcher_wait_returncode": 1,
      "DONE_sha256": "3db423dee4828d5439478063739e07a774167e131978f73f76cef915d22d3580",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-769e6d9fd5f9cd53-CH",
      "uuid": "0b3b03d2-1cfd-46d2-adc8-721c5e51c4f2",
      "program": "GESUMMV",
      "arm": "CH",
      "input_digest": "769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4",
      "model": {
        "pid": 1261785,
        "requested_start_ticks": 968882839,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-769e6d9fd5f9cd53-CH.RESULT.json",
      "launcher": {
        "pid": 1261779,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 16,
        "instructions": 190918656,
        "kernels": 1
      },
      "recorded_stop_reason": "DTC_ORIGINAL_RESOURCE_POLICY:CURRENT_GUARD:expected_growth",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "5d24f255e24ebda8fc4996734afa5c4b3a249837c56f50d1570f89b13b9a288a",
      "category": "NATIVE_FAILURE_UNACCEPTED",
      "independent_negative_closure": {
        "path": "/root/data/dtc_failure_repair_20261025_v1/analysis/gesummv_expected_growth_metadata_closure_v1/0b3b03d2-1cfd-46d2-adc8-721c5e51c4f2/POSTPROCESS.RESULT.json",
        "sha256": "cb86b7bbedc6021e4eadf0b9d2a4dfa8cde4af5350eea07bbf689f9ab0176583",
        "old_canonical_RESULT_preserved": true,
        "accepted_cycles": null
      }
    },
    {
      "cohort": "E2-AEV100-977e34578994c3d2-CH",
      "uuid": "a0a7bcfa-91d9-4498-aa2b-c18f9e696dc8",
      "program": "myocyte",
      "arm": "CH",
      "input_digest": "977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992",
      "model": {
        "pid": 1062441,
        "requested_start_ticks": 962161766,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-977e34578994c3d2-CH.RESULT.json",
      "launcher": {
        "pid": 1062436,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 11986,
        "instructions": 42921588,
        "kernels": 5993
      },
      "recorded_stop_reason": "DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "8ef4b128f2d88b75786484325bfde2075246f0667a2a5e12a6d949efb0ea9257",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-977e34578994c3d2-DM",
      "uuid": "95fedea6-6293-4673-9150-e36822857be0",
      "program": "myocyte",
      "arm": "DM",
      "input_digest": "977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992",
      "model": {
        "pid": 1069239,
        "requested_start_ticks": 962248392,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-977e34578994c3d2-DM.RESULT.json",
      "launcher": {
        "pid": 1069234,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 11986,
        "instructions": 42921588,
        "kernels": 5993
      },
      "recorded_stop_reason": "DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "1783bc6d14bdba68ce70df4c6332c106f22e4e81d71e513386f675fc2f4bf63d",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-ddb6806316876a85-CH",
      "uuid": "b6e28445-8e1b-48fd-b352-aeca570bff64",
      "program": "lavamd",
      "arm": "CH",
      "input_digest": "ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8",
      "model": {
        "pid": 1269742,
        "requested_start_ticks": 969082348,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-ddb6806316876a85-CH.RESULT.json",
      "launcher": {
        "pid": 1269737,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 1000,
        "instructions": 10396775488,
        "kernels": 1
      },
      "recorded_stop_reason": "DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "df5125884f52ad654bdac2d2be5e86a644aadf7fc572d3b566b772e6c6a41f72",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-ddb6806316876a85-CM",
      "uuid": "eaa858dd-04d0-41ba-9a3c-a5975c330720",
      "program": "lavamd",
      "arm": "CM",
      "input_digest": "ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8",
      "model": {
        "pid": 1264151,
        "requested_start_ticks": 968946970,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-ddb6806316876a85-CM.RESULT.json",
      "launcher": {
        "pid": 1264146,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 1000,
        "instructions": 10396775488,
        "kernels": 1
      },
      "recorded_stop_reason": "DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "bf294600c23b02876b4c2faf7542b2999b0e6475be6a0e015eea6ca3c8c8dd56",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-ddb6806316876a85-DH",
      "uuid": "545822b7-d775-4525-ace4-16825c3ea25b",
      "program": "lavamd",
      "arm": "DH",
      "input_digest": "ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8",
      "model": {
        "pid": 1361326,
        "requested_start_ticks": 972659929,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-ddb6806316876a85-DH.RESULT.json",
      "launcher": {
        "pid": 1361321,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 1000,
        "instructions": 10396775488,
        "kernels": 1
      },
      "recorded_stop_reason": "DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "568643e4160461061b7f6c2918dc562abd47ffd64468e1d68e54f2889b5cdc15",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-e7bb67e63e3c3847-DH",
      "uuid": "b15d3469-ed1b-4979-b7fa-9ba864c8630e",
      "program": "vectorAdd",
      "arm": "DH",
      "input_digest": "e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799",
      "model": {
        "pid": 1192249,
        "requested_start_ticks": 965853383,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-e7bb67e63e3c3847-DH.RESULT.json",
      "launcher": {
        "pid": 1192244,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 23438,
        "instructions": 84000768,
        "kernels": 1
      },
      "recorded_stop_reason": "MEMORY_HEADROOM",
      "launcher_wait_returncode": -15,
      "DONE_sha256": "ec54d92fe1e2a80418a16b7b6323fb3a3241ec3f9b820a606682ef3eb0350b15",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-e9110566572e0e0d-DH",
      "uuid": "b91f0981-33c3-41e5-983f-9cdd4ecadf87",
      "program": "hybridsort",
      "arm": "DH",
      "input_digest": "e9110566572e0e0dd3c00afc3aba533fa14ca3bb53a52cb44ffb4262b67be967",
      "model": {
        "pid": 1287288,
        "requested_start_ticks": 969709691,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-e9110566572e0e0d-DH.RESULT.json",
      "launcher": {
        "pid": 1287283,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 18260,
        "instructions": 623276352,
        "kernels": 56
      },
      "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
      "launcher_wait_returncode": 1,
      "DONE_sha256": "d9d9f4d92a3cc9c3511c2855c7c67678efa0feac145ca1c535906bc6c571789a",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-e9110566572e0e0d-DM",
      "uuid": "2ca00227-7ea3-4ada-a79f-eb1ddd56e7d6",
      "program": "hybridsort",
      "arm": "DM",
      "input_digest": "e9110566572e0e0dd3c00afc3aba533fa14ca3bb53a52cb44ffb4262b67be967",
      "model": {
        "pid": 1287939,
        "requested_start_ticks": 969732515,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": true,
      "NATIVE_EXIT_exists": true,
      "registry_execution_receipt_exists": true,
      "result_state": "FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-e9110566572e0e0d-DM.RESULT.json",
      "launcher": {
        "pid": 1287934,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 18260,
        "instructions": 623276352,
        "kernels": 56
      },
      "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
      "launcher_wait_returncode": 1,
      "DONE_sha256": "af465537e7f6cf7605a0860c82bda4816615b1d1f5fcf708bde5f24264b35449",
      "category": "NATIVE_FAILURE_UNACCEPTED"
    }
  ],
  "missing_observer_receipts": [
    {
      "cohort": "E2-AEV100-09f94fcc7494a03b-CM",
      "uuid": "df5fda68-3c3d-4b37-844f-d7ea6a1d5293",
      "program": "hybridsort",
      "arm": "CM",
      "input_digest": "09f94fcc7494a03b160b40b705cbc7ff5f41e88e8ee417d187e5c7fbcac82123",
      "model": {
        "pid": 1264727,
        "requested_start_ticks": 968963653,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": "ENGINEERING_MODEL_GONE_RECEIPT_MISSING_PRESERVED",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-09f94fcc7494a03b-CM.RESULT.json",
      "launcher": {
        "pid": 1264722,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 115324,
        "instructions": 6276086260,
        "kernels": 68
      },
      "category": "MISSING_OBSERVER_RECEIPT_GONE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-85700545918390d7-DM",
      "uuid": "97c43b01-9628-490f-839e-4a2a8126122e",
      "program": "cfd",
      "arm": "DM",
      "input_digest": "85700545918390d7a5cb33340f2043b13bf86a86d6141de238916cc60eb941cd",
      "model": {
        "pid": 1263485,
        "requested_start_ticks": 968923826,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": "RESOLVING_ISSUE_NO_MODEL_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-85700545918390d7-DM.RESULT.json",
      "launcher": {
        "pid": 1263480,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 6060,
        "instructions": 343346212,
        "kernels": 5
      },
      "category": "MISSING_OBSERVER_RECEIPT_GONE_UNACCEPTED"
    },
    {
      "cohort": "E2-AEV100-e7c791ce2e4b09ee-DM",
      "uuid": "f6c79f5f-6b0e-42d7-a5be-c3013fa7aaba",
      "program": "b+tree",
      "arm": "DM",
      "input_digest": "e7c791ce2e4b09eea844428fdf220e0d3f095783c022a60aa9186c6146ddd83c",
      "model": {
        "pid": 1270448,
        "requested_start_ticks": 969104373,
        "alive": false,
        "proc_absent": true
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": "RESOLVING_ISSUE_NO_MODEL_RETRY",
      "result_path": "/root/data/dtc_main_v100_sweep_20261025_v1/analysis/E2-AEV100-e7c791ce2e4b09ee-DM.RESULT.json",
      "launcher": {
        "pid": 1270443,
        "requested_start_ticks": null,
        "alive": false,
        "proc_absent": true
      },
      "expected": {
        "CTA": 16000,
        "instructions": 444467849,
        "kernels": 2
      },
      "category": "MISSING_OBSERVER_RECEIPT_GONE_UNACCEPTED"
    }
  ],
  "live": [
    {
      "cohort": "E2-AEV100-1213f9ab49665a65-CH",
      "uuid": "1c982147-a201-43f4-813c-7307ddc124fb",
      "program": "kmeans",
      "arm": "CH",
      "input_digest": "1213f9ab49665a65b429c79e0511047e92524e5f9bf53cc706ab222af22634aa",
      "model": {
        "pid": 1292091,
        "start_ticks": 969830705,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          80
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1292086,
        "start_ticks": 969830705,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 9747,
        "instructions": 2165609728,
        "kernels": 3
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-CH",
      "uuid": "97f34f82-2c2e-4c1d-8092-6ad1fa149126",
      "program": "kmeans",
      "arm": "CH",
      "input_digest": "2315d0e612ee7cd4ee6e711e2a673e85d7490bec9a8767ec67bde3ddafff970a",
      "model": {
        "pid": 1264276,
        "start_ticks": 968951274,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          79
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1264271,
        "start_ticks": 968951274,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 5808,
        "instructions": 1305753912,
        "kernels": 3
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-CM",
      "uuid": "d72700d7-cc77-411f-af13-a3653df8170d",
      "program": "kmeans",
      "arm": "CM",
      "input_digest": "2315d0e612ee7cd4ee6e711e2a673e85d7490bec9a8767ec67bde3ddafff970a",
      "model": {
        "pid": 1361316,
        "start_ticks": 972659792,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          72
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1361311,
        "start_ticks": 972659792,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 5808,
        "instructions": 1305753912,
        "kernels": 3
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-DH",
      "uuid": "b52d5c8c-27a2-48d3-a2c8-70fe4814d098",
      "program": "kmeans",
      "arm": "DH",
      "input_digest": "2315d0e612ee7cd4ee6e711e2a673e85d7490bec9a8767ec67bde3ddafff970a",
      "model": {
        "pid": 1361466,
        "start_ticks": 972664497,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          71
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1361461,
        "start_ticks": 972664496,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 5808,
        "instructions": 1305753912,
        "kernels": 3
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-DM",
      "uuid": "29cf62cb-5af3-4743-b221-472e8d6e80b2",
      "program": "kmeans",
      "arm": "DM",
      "input_digest": "2315d0e612ee7cd4ee6e711e2a673e85d7490bec9a8767ec67bde3ddafff970a",
      "model": {
        "pid": 1362999,
        "start_ticks": 972722142,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          73
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1362994,
        "start_ticks": 972722141,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 5808,
        "instructions": 1305753912,
        "kernels": 3
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-79f8ab6241faeed6-CH",
      "uuid": "cb0e9736-e699-4a1a-b8b8-386f18a11698",
      "program": "3DCONV",
      "arm": "CH",
      "input_digest": "79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d",
      "model": {
        "pid": 1359774,
        "start_ticks": 972623382,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          70
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1359769,
        "start_ticks": 972623381,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 65024,
        "instructions": 823239400,
        "kernels": 254
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-79f8ab6241faeed6-DH",
      "uuid": "68e9d9b1-2e63-4310-bc1b-1805fc3a9940",
      "program": "3DCONV",
      "arm": "DH",
      "input_digest": "79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d",
      "model": {
        "pid": 1360633,
        "start_ticks": 972641433,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          65
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1360628,
        "start_ticks": 972641432,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 65024,
        "instructions": 823239400,
        "kernels": 254
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-CM",
      "uuid": "89539cb0-0a41-402a-b19d-ca3b266ef263",
      "program": "SYRK",
      "arm": "CM",
      "input_digest": "b51811aca9dc70cfe109fad8de73d5305647bc16d70b9289c1c918f4d3ab5d39",
      "model": {
        "pid": 1285886,
        "start_ticks": 969646089,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          81
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1285881,
        "start_ticks": 969646089,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 4096,
        "instructions": 5626658816,
        "kernels": 1
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-DH",
      "uuid": "369ccba9-9ad9-407f-916b-5925044bdd6a",
      "program": "SYRK",
      "arm": "DH",
      "input_digest": "b51811aca9dc70cfe109fad8de73d5305647bc16d70b9289c1c918f4d3ab5d39",
      "model": {
        "pid": 1287678,
        "start_ticks": 969722549,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          82
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1287673,
        "start_ticks": 969722548,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 4096,
        "instructions": 5626658816,
        "kernels": 1
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-DM",
      "uuid": "04864616-6e93-422e-bf42-a2137574c43d",
      "program": "SYRK",
      "arm": "DM",
      "input_digest": "b51811aca9dc70cfe109fad8de73d5305647bc16d70b9289c1c918f4d3ab5d39",
      "model": {
        "pid": 1262476,
        "start_ticks": 968887690,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          94
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1262471,
        "start_ticks": 968887689,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 4096,
        "instructions": 5626658816,
        "kernels": 1
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-f7d6397ed7ffa266-DH",
      "uuid": "c8310119-44a7-44de-ae3b-bb8c4e5c684a",
      "program": "streamcluster",
      "arm": "DH",
      "input_digest": "f7d6397ed7ffa266724e124e76e896015cd71a9936a43e787d815c3c8420f348",
      "model": {
        "pid": 1285471,
        "start_ticks": 969626083,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          68
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1285466,
        "start_ticks": 969626082,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 640,
        "instructions": 577714898,
        "kernels": 5
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-f7d6397ed7ffa266-DM",
      "uuid": "c4a7e61b-83b0-46e2-81e4-02034124f0f0",
      "program": "streamcluster",
      "arm": "DM",
      "input_digest": "f7d6397ed7ffa266724e124e76e896015cd71a9936a43e787d815c3c8420f348",
      "model": {
        "pid": 1285479,
        "start_ticks": 969626098,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          69
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1285474,
        "start_ticks": 969626097,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 640,
        "instructions": 577714898,
        "kernels": 5
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-fc0705ae3721e999-CH",
      "uuid": "df58f975-ac7a-4735-81de-3512ff585c67",
      "program": "GEMM",
      "arm": "CH",
      "input_digest": "fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318",
      "model": {
        "pid": 1355741,
        "start_ticks": 972480598,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          66
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1355736,
        "start_ticks": 972480597,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 1024,
        "instructions": 739246080,
        "kernels": 1
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-fc0705ae3721e999-DH",
      "uuid": "2261440b-c603-454c-8698-6a2d3caaefe8",
      "program": "GEMM",
      "arm": "DH",
      "input_digest": "fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318",
      "model": {
        "pid": 1356945,
        "start_ticks": 972536954,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          67
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1356940,
        "start_ticks": 972536953,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 1024,
        "instructions": 739246080,
        "kernels": 1
      },
      "category": "LIVE"
    },
    {
      "cohort": "E2-AEV100-fc0705ae3721e999-DM",
      "uuid": "8547fd04-5869-406b-b3a8-d64949c8f9ef",
      "program": "GEMM",
      "arm": "DM",
      "input_digest": "fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318",
      "model": {
        "pid": 1359687,
        "start_ticks": 972621609,
        "state": "R",
        "same_generation": true,
        "alive": true,
        "actual_CPU_affinity": [
          64
        ]
      },
      "DONE_exists": false,
      "NATIVE_EXIT_exists": false,
      "registry_execution_receipt_exists": false,
      "result_state": null,
      "result_path": null,
      "launcher": {
        "pid": 1359682,
        "start_ticks": 972621608,
        "state": "S",
        "same_generation": true,
        "alive": true
      },
      "expected": {
        "CTA": 1024,
        "instructions": 739246080,
        "kernels": 1
      },
      "category": "LIVE"
    }
  ],
  "PASS_cohorts": [
    "E2-AEV100-030e87a45e9c6dae-CH",
    "E2-AEV100-030e87a45e9c6dae-CM",
    "E2-AEV100-030e87a45e9c6dae-DH",
    "E2-AEV100-030e87a45e9c6dae-DM",
    "E2-AEV100-0323e504fc928c58-CH",
    "E2-AEV100-0323e504fc928c58-CM",
    "E2-AEV100-0323e504fc928c58-DH",
    "E2-AEV100-0323e504fc928c58-DM",
    "E2-AEV100-0e62c67daa020853-DM",
    "E2-AEV100-1299a96e35024a59-CH",
    "E2-AEV100-1299a96e35024a59-CM",
    "E2-AEV100-1299a96e35024a59-DH",
    "E2-AEV100-1299a96e35024a59-DM",
    "E2-AEV100-16f4c42373e4961e-CH",
    "E2-AEV100-16f4c42373e4961e-CM",
    "E2-AEV100-16f4c42373e4961e-DH",
    "E2-AEV100-16f4c42373e4961e-DM",
    "E2-AEV100-196006754730d8ab-CH",
    "E2-AEV100-196006754730d8ab-CM",
    "E2-AEV100-196006754730d8ab-DH",
    "E2-AEV100-196006754730d8ab-DM",
    "E2-AEV100-1df9d5479504d9c7-CH",
    "E2-AEV100-1df9d5479504d9c7-CM",
    "E2-AEV100-2982f1db6fe84971-CH",
    "E2-AEV100-2982f1db6fe84971-CM",
    "E2-AEV100-2982f1db6fe84971-DH",
    "E2-AEV100-2982f1db6fe84971-DM",
    "E2-AEV100-2b93f70cd0666c51-CH",
    "E2-AEV100-2b93f70cd0666c51-DM",
    "E2-AEV100-2c506bf13c81ff5d-CH",
    "E2-AEV100-2c506bf13c81ff5d-CM",
    "E2-AEV100-322bdf9f1830fad4-CH",
    "E2-AEV100-322bdf9f1830fad4-CM",
    "E2-AEV100-322bdf9f1830fad4-DH",
    "E2-AEV100-322bdf9f1830fad4-DM",
    "E2-AEV100-36b09814c609253d-CH",
    "E2-AEV100-36b09814c609253d-CM",
    "E2-AEV100-36b09814c609253d-DH",
    "E2-AEV100-36b09814c609253d-DM",
    "E2-AEV100-3722a5c85d91a948-CH",
    "E2-AEV100-3722a5c85d91a948-CM",
    "E2-AEV100-3722a5c85d91a948-DH",
    "E2-AEV100-3722a5c85d91a948-DM",
    "E2-AEV100-3aac3b722c1b2e50-CH",
    "E2-AEV100-3aac3b722c1b2e50-CM",
    "E2-AEV100-3aac3b722c1b2e50-DH",
    "E2-AEV100-3aac3b722c1b2e50-DM",
    "E2-AEV100-3f85d1878aba9f04-CH",
    "E2-AEV100-3f85d1878aba9f04-CM",
    "E2-AEV100-3f85d1878aba9f04-DH",
    "E2-AEV100-3f85d1878aba9f04-DM",
    "E2-AEV100-4114a3dc0d06b55b-CH",
    "E2-AEV100-4114a3dc0d06b55b-CM",
    "E2-AEV100-4114a3dc0d06b55b-DH",
    "E2-AEV100-4114a3dc0d06b55b-DM",
    "E2-AEV100-45cba351972ddf30-CH",
    "E2-AEV100-45cba351972ddf30-CM",
    "E2-AEV100-45cba351972ddf30-DH",
    "E2-AEV100-45cba351972ddf30-DM",
    "E2-AEV100-4683a782a4ece0d9-CH",
    "E2-AEV100-4683a782a4ece0d9-CM",
    "E2-AEV100-4683a782a4ece0d9-DH",
    "E2-AEV100-4683a782a4ece0d9-DM",
    "E2-AEV100-59908b3dd7cb0a0e-CH",
    "E2-AEV100-59908b3dd7cb0a0e-CM",
    "E2-AEV100-59908b3dd7cb0a0e-DH",
    "E2-AEV100-59908b3dd7cb0a0e-DM",
    "E2-AEV100-5fa6f81161d230f5-CH",
    "E2-AEV100-5fa6f81161d230f5-CM",
    "E2-AEV100-5fa6f81161d230f5-DH",
    "E2-AEV100-5fa6f81161d230f5-DM",
    "E2-AEV100-64da93d5cac47cd5-CH",
    "E2-AEV100-64da93d5cac47cd5-CM",
    "E2-AEV100-64da93d5cac47cd5-DH",
    "E2-AEV100-64da93d5cac47cd5-DM",
    "E2-AEV100-65151d2c661f88f3-CH",
    "E2-AEV100-65151d2c661f88f3-CM",
    "E2-AEV100-65151d2c661f88f3-DH",
    "E2-AEV100-65151d2c661f88f3-DM",
    "E2-AEV100-66a2ff40b5b4f8da-CH",
    "E2-AEV100-66a2ff40b5b4f8da-CM",
    "E2-AEV100-66a2ff40b5b4f8da-DH",
    "E2-AEV100-66a2ff40b5b4f8da-DM",
    "E2-AEV100-6811f98b1edd34f6-CH",
    "E2-AEV100-6811f98b1edd34f6-CM",
    "E2-AEV100-6811f98b1edd34f6-DH",
    "E2-AEV100-6811f98b1edd34f6-DM",
    "E2-AEV100-6dad43cf98e66240-CH",
    "E2-AEV100-6dad43cf98e66240-CM",
    "E2-AEV100-6dad43cf98e66240-DH",
    "E2-AEV100-6dad43cf98e66240-DM",
    "E2-AEV100-6e35d612712f2706-CH",
    "E2-AEV100-6e35d612712f2706-CM",
    "E2-AEV100-6e35d612712f2706-DH",
    "E2-AEV100-6e35d612712f2706-DM",
    "E2-AEV100-731af5428c4b8155-CH",
    "E2-AEV100-731af5428c4b8155-CM",
    "E2-AEV100-731af5428c4b8155-DH",
    "E2-AEV100-731af5428c4b8155-DM",
    "E2-AEV100-7530ee6952c967c5-CH",
    "E2-AEV100-7530ee6952c967c5-CM",
    "E2-AEV100-7530ee6952c967c5-DH",
    "E2-AEV100-7530ee6952c967c5-DM",
    "E2-AEV100-769e6d9fd5f9cd53-CM",
    "E2-AEV100-769e6d9fd5f9cd53-DH",
    "E2-AEV100-769e6d9fd5f9cd53-DM",
    "E2-AEV100-786d2bd637e41534-CH",
    "E2-AEV100-786d2bd637e41534-CM",
    "E2-AEV100-786d2bd637e41534-DH",
    "E2-AEV100-786d2bd637e41534-DM",
    "E2-AEV100-79f8ab6241faeed6-CM",
    "E2-AEV100-79f8ab6241faeed6-DM",
    "E2-AEV100-85700545918390d7-CH",
    "E2-AEV100-85700545918390d7-CM",
    "E2-AEV100-85700545918390d7-DH",
    "E2-AEV100-8df9ee2d901953e7-CH",
    "E2-AEV100-8df9ee2d901953e7-CM",
    "E2-AEV100-8df9ee2d901953e7-DH",
    "E2-AEV100-8df9ee2d901953e7-DM",
    "E2-AEV100-977a2f7007cb1f96-CH",
    "E2-AEV100-977a2f7007cb1f96-DH",
    "E2-AEV100-977e34578994c3d2-CM",
    "E2-AEV100-977e34578994c3d2-DH",
    "E2-AEV100-9e80de77fd34591f-CH",
    "E2-AEV100-9e80de77fd34591f-CM",
    "E2-AEV100-9e80de77fd34591f-DH",
    "E2-AEV100-9e80de77fd34591f-DM",
    "E2-AEV100-ae34174fbbdf83b2-CH",
    "E2-AEV100-ae34174fbbdf83b2-CM",
    "E2-AEV100-ae34174fbbdf83b2-DH",
    "E2-AEV100-ae34174fbbdf83b2-DM",
    "E2-AEV100-b31a85e4eb8d32ef-CH",
    "E2-AEV100-b31a85e4eb8d32ef-CM",
    "E2-AEV100-b31a85e4eb8d32ef-DH",
    "E2-AEV100-b31a85e4eb8d32ef-DM",
    "E2-AEV100-b33381cf25d44359-CH",
    "E2-AEV100-b33381cf25d44359-CM",
    "E2-AEV100-b33381cf25d44359-DH",
    "E2-AEV100-b33381cf25d44359-DM",
    "E2-AEV100-b41cc74c66ca6ed4-CH",
    "E2-AEV100-b41cc74c66ca6ed4-CM",
    "E2-AEV100-b41cc74c66ca6ed4-DH",
    "E2-AEV100-b41cc74c66ca6ed4-DM",
    "E2-AEV100-bd8f42c4d21e28ce-CH",
    "E2-AEV100-bd8f42c4d21e28ce-CM",
    "E2-AEV100-bd8f42c4d21e28ce-DH",
    "E2-AEV100-bd8f42c4d21e28ce-DM",
    "E2-AEV100-c7efba60561811c0-CH",
    "E2-AEV100-c7efba60561811c0-CM",
    "E2-AEV100-c7efba60561811c0-DH",
    "E2-AEV100-c7efba60561811c0-DM",
    "E2-AEV100-c885293ad99e21ee-CH",
    "E2-AEV100-c885293ad99e21ee-DM",
    "E2-AEV100-ccdd1b98bff6187e-CH",
    "E2-AEV100-ccdd1b98bff6187e-CM",
    "E2-AEV100-ccdd1b98bff6187e-DH",
    "E2-AEV100-ccdd1b98bff6187e-DM",
    "E2-AEV100-cf569ed4fa54b5f1-CH",
    "E2-AEV100-cf569ed4fa54b5f1-CM",
    "E2-AEV100-cf569ed4fa54b5f1-DH",
    "E2-AEV100-cf569ed4fa54b5f1-DM",
    "E2-AEV100-d984ea5475a581ad-CH",
    "E2-AEV100-d984ea5475a581ad-CM",
    "E2-AEV100-d984ea5475a581ad-DH",
    "E2-AEV100-d984ea5475a581ad-DM",
    "E2-AEV100-db89be14146b9163-CH",
    "E2-AEV100-db89be14146b9163-CM",
    "E2-AEV100-db89be14146b9163-DH",
    "E2-AEV100-db89be14146b9163-DM",
    "E2-AEV100-dc7a91531846c113-CH",
    "E2-AEV100-dc7a91531846c113-CM",
    "E2-AEV100-dc7a91531846c113-DH",
    "E2-AEV100-dc7a91531846c113-DM",
    "E2-AEV100-dd8955feff97ab8c-CH",
    "E2-AEV100-dd8955feff97ab8c-CM",
    "E2-AEV100-dd8955feff97ab8c-DH",
    "E2-AEV100-dd8955feff97ab8c-DM",
    "E2-AEV100-dd9f695c4f53b083-CH",
    "E2-AEV100-dd9f695c4f53b083-CM",
    "E2-AEV100-dd9f695c4f53b083-DH",
    "E2-AEV100-dd9f695c4f53b083-DM",
    "E2-AEV100-e5638b94095098ac-CH",
    "E2-AEV100-e5638b94095098ac-CM",
    "E2-AEV100-e5638b94095098ac-DH",
    "E2-AEV100-e5638b94095098ac-DM",
    "E2-AEV100-e7bb67e63e3c3847-CH",
    "E2-AEV100-e7bb67e63e3c3847-CM",
    "E2-AEV100-e7bb67e63e3c3847-DM",
    "E2-AEV100-e7c791ce2e4b09ee-CH",
    "E2-AEV100-e7c791ce2e4b09ee-CM",
    "E2-AEV100-e7c791ce2e4b09ee-DH",
    "E2-AEV100-e9110566572e0e0d-CH",
    "E2-AEV100-e9110566572e0e0d-CM",
    "E2-AEV100-ec1461f2c83fe1bd-CH",
    "E2-AEV100-ec1461f2c83fe1bd-CM",
    "E2-AEV100-ec1461f2c83fe1bd-DH",
    "E2-AEV100-ec1461f2c83fe1bd-DM",
    "E2-AEV100-eededb785179fc04-CH",
    "E2-AEV100-eededb785179fc04-CM",
    "E2-AEV100-eededb785179fc04-DH",
    "E2-AEV100-eededb785179fc04-DM",
    "E2-AEV100-f437190767aaed49-CH",
    "E2-AEV100-f437190767aaed49-CM",
    "E2-AEV100-f437190767aaed49-DH",
    "E2-AEV100-f437190767aaed49-DM",
    "E2-AEV100-f7d6397ed7ffa266-CH",
    "E2-AEV100-f7d6397ed7ffa266-CM",
    "E2-AEV100-f7f22a2ccc836a8a-CH",
    "E2-AEV100-f7f22a2ccc836a8a-CM",
    "E2-AEV100-f7f22a2ccc836a8a-DH",
    "E2-AEV100-f7f22a2ccc836a8a-DM",
    "E2-AEV100-f9edab43938e7bf4-CH",
    "E2-AEV100-f9edab43938e7bf4-CM",
    "E2-AEV100-f9edab43938e7bf4-DH",
    "E2-AEV100-f9edab43938e7bf4-DM",
    "E2-AEV100-facf277aaa8e806d-CH",
    "E2-AEV100-facf277aaa8e806d-CM",
    "E2-AEV100-facf277aaa8e806d-DH",
    "E2-AEV100-facf277aaa8e806d-DM",
    "E2-AEV100-fc0705ae3721e999-CM",
    "E2-AEV100-fd0772a865199cad-CH",
    "E2-AEV100-fd0772a865199cad-CM",
    "E2-AEV100-fd0772a865199cad-DH",
    "E2-AEV100-fd0772a865199cad-DM",
    "E2-AEV100-ffc8a89493c8a211-CH",
    "E2-AEV100-ffc8a89493c8a211-CM",
    "E2-AEV100-ffc8a89493c8a211-DM",
    "E2-AEV100-fff1afd00c2eb305-CH",
    "E2-AEV100-fff1afd00c2eb305-CM",
    "E2-AEV100-fff1afd00c2eb305-DH",
    "E2-AEV100-fff1afd00c2eb305-DM"
  ],
  "other_pending": []
}
```

### repairs

```json
{
  "DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1": {
    "root": "/root/data/dtc_failure_repair_20261025_v1/validation",
    "registered_budget": 23,
    "remaining": 0,
    "consumed": 23,
    "registry_state": "CLOSED",
    "registry_validation_status": "CLOSED_WITH_ARCHIVED_FAILURES",
    "point_counts": {
      "PASS_CORRECTNESS_VALIDATION_ONLY": 21,
      "NATIVE_FAILURE_UNACCEPTED": 2
    },
    "preserved_R14_canonical_counts": {
      "PASS": 11,
      "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE": 10,
      "NATIVE_FAILURE_UNACCEPTED": 2
    },
    "points": [
      {
        "cohort": "E2-AEREPAIR-09f94fcc7494a03b-DH-V1",
        "uuid": "864786c9-7e43-49d9-8c5b-8e008d980cfd",
        "program": "hybridsort",
        "arm": "DH",
        "input_digest": "09f94fcc7494a03b160b40b705cbc7ff5f41e88e8ee417d187e5c7fbcac82123",
        "model": {
          "pid": 1289581,
          "requested_start_ticks": 969763364,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-09f94fcc7494a03b-DH-V1.RESULT.json",
        "launcher": {
          "pid": 1289576,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 115324,
          "instructions": 6276086260,
          "kernels": 68
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "0d2bc24b2c77d4449a04af52fdc78e1a6e7273a7f9898880585b30d506af60e8",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-09f94fcc7494a03b-DM-V1",
        "uuid": "ea54ebef-1873-4c57-9863-6629c1aa0305",
        "program": "hybridsort",
        "arm": "DM",
        "input_digest": "09f94fcc7494a03b160b40b705cbc7ff5f41e88e8ee417d187e5c7fbcac82123",
        "model": {
          "pid": 1289755,
          "requested_start_ticks": 969764943,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-09f94fcc7494a03b-DM-V1.RESULT.json",
        "launcher": {
          "pid": 1289750,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 115324,
          "instructions": 6276086260,
          "kernels": 68
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "140aafde706220e6a1100ada938b8e4fc196acea7e82e14953bf8f4a4fde4909",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-1df9d5479504d9c7-DH-V1",
        "uuid": "9d86d6e0-7005-4314-9248-bf09cb6e6fcc",
        "program": "bfs",
        "arm": "DH",
        "input_digest": "1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0",
        "model": {
          "pid": 1289529,
          "requested_start_ticks": 969763265,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-1df9d5479504d9c7-DH-V1.RESULT.json",
        "launcher": {
          "pid": 1289524,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 76,
          "instructions": 121542388,
          "kernels": 11
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "23bc36523d28d995d5cbecff8a098e57c72643abb21d18a3e4b7d78c2a8732be",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-1df9d5479504d9c7-DM-V1",
        "uuid": "7ff782f3-0828-433c-a2cf-39854086ca01",
        "program": "bfs",
        "arm": "DM",
        "input_digest": "1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0",
        "model": {
          "pid": 1289536,
          "requested_start_ticks": 969763270,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-1df9d5479504d9c7-DM-V1.RESULT.json",
        "launcher": {
          "pid": 1289531,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 76,
          "instructions": 121542388,
          "kernels": 11
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "54942f851a4541d419ea3cf921fd77404915e745322e8db4726b808b603b1e2a",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-2b93f70cd0666c51-DH-V1",
        "uuid": "8f591968-b326-41b0-b52f-14182e81e21b",
        "program": "scalarProd",
        "arm": "DH",
        "input_digest": "2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954",
        "model": {
          "pid": 1289563,
          "requested_start_ticks": 969763313,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-2b93f70cd0666c51-DH-V1.RESULT.json",
        "launcher": {
          "pid": 1289558,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 128,
          "instructions": 730610912,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "f762cba44975d399194e3d385a1580370c61e64b3898f7e5b091912989871425",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-2c506bf13c81ff5d-DM-V1",
        "uuid": "5678a8d9-1347-41f6-af70-83e33b6aac99",
        "program": "histo",
        "arm": "DM",
        "input_digest": "2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64",
        "model": {
          "pid": 1289575,
          "requested_start_ticks": 969763343,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-2c506bf13c81ff5d-DM-V1.RESULT.json",
        "launcher": {
          "pid": 1289570,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 4260,
          "instructions": 2196264084,
          "kernels": 80
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "71e5c76a0423fc2ef7521a97e206a4a38b0b41074af11a4bd4ef2400b914c256",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-85700545918390d7-DM-V1",
        "uuid": "9c527401-db72-4098-941c-92efc0189045",
        "program": "cfd",
        "arm": "DM",
        "input_digest": "85700545918390d7a5cb33340f2043b13bf86a86d6141de238916cc60eb941cd",
        "model": {
          "pid": 1289545,
          "requested_start_ticks": 969763282,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-85700545918390d7-DM-V1.RESULT.json",
        "launcher": {
          "pid": 1289540,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 6060,
          "instructions": 343346212,
          "kernels": 5
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "6e4be3ae16f4c31bcbbb02839a4658721abe6611c4bcb61e75de956a5bb012d0",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-977e34578994c3d2-CH-V1",
        "uuid": "c9eb2ddd-b7e9-4367-bbba-fd7096f01f7f",
        "program": "myocyte",
        "arm": "CH",
        "input_digest": "977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992",
        "model": {
          "pid": 1290160,
          "requested_start_ticks": 969782001,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-977e34578994c3d2-CH-V1.RESULT.json",
        "launcher": {
          "pid": 1290155,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 11986,
          "instructions": 42921588,
          "kernels": 5993
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "2d48dfe740f1b8bfd03deea17eaab5a4a6ed845a1f4f6229f37831031237973d",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-977e34578994c3d2-DM-V1",
        "uuid": "dea19059-ef8c-4ab8-86e1-d86b19b50b6b",
        "program": "myocyte",
        "arm": "DM",
        "input_digest": "977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992",
        "model": {
          "pid": 1290166,
          "requested_start_ticks": 969782005,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-977e34578994c3d2-DM-V1.RESULT.json",
        "launcher": {
          "pid": 1290161,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 11986,
          "instructions": 42921588,
          "kernels": 5993
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "2132023f20f1829571a10f899f351504ad2757c9a69f62c30e43b86c12585b4f",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-BASE-V1",
        "uuid": "4a19a751-da84-4d11-ae33-eb183e715256",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:VECTORADD_ORIGINAL4M",
        "arm": "BASE",
        "input_digest": "3375b4a8feb883fc39f2a7777d224f921a1ecd9ff3d624654a0c69efab0a0d09",
        "model": {
          "pid": 1289472,
          "requested_start_ticks": 969763185,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-3375b4a8feb883fc-BASE-V1.RESULT.json",
        "launcher": {
          "pid": 1289466,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 15625,
          "instructions": 56000000,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "d35344f22dca80dba9fd99f11be9a7611d45fd2fee289a0020ec9422afde4624",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-IO-V1",
        "uuid": "2d592f9b-06b2-4389-b685-e01d5e7900e1",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:VECTORADD_ORIGINAL4M",
        "arm": "IO",
        "input_digest": "3375b4a8feb883fc39f2a7777d224f921a1ecd9ff3d624654a0c69efab0a0d09",
        "model": {
          "pid": 1289488,
          "requested_start_ticks": 969763192,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-3375b4a8feb883fc-IO-V1.RESULT.json",
        "launcher": {
          "pid": 1289482,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 15625,
          "instructions": 56000000,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "655080ae80805587876c6b2266eff891839e6737aa497031412d228643ee1220",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-LEGACY-V1",
        "uuid": "cf9404f2-1e13-4cc3-8fca-ecf536d25a26",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:VECTORADD_ORIGINAL4M",
        "arm": "LEGACY",
        "input_digest": "3375b4a8feb883fc39f2a7777d224f921a1ecd9ff3d624654a0c69efab0a0d09",
        "model": {
          "pid": 1289496,
          "requested_start_ticks": 969763205,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-3375b4a8feb883fc-LEGACY-V1.RESULT.json",
        "launcher": {
          "pid": 1289491,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 15625,
          "instructions": 56000000,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "a9439b5a8ea68b7713ea941d50e0d6743284f91335641cc03f34aa86eadeea6b",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-OO-V1",
        "uuid": "d8e529fb-c282-423e-880f-4d574cf7e1df",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:VECTORADD_ORIGINAL4M",
        "arm": "OO",
        "input_digest": "3375b4a8feb883fc39f2a7777d224f921a1ecd9ff3d624654a0c69efab0a0d09",
        "model": {
          "pid": 1289502,
          "requested_start_ticks": 969763217,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-3375b4a8feb883fc-OO-V1.RESULT.json",
        "launcher": {
          "pid": 1289497,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 15625,
          "instructions": 56000000,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "e7130bb5619ce091967118f14616296ac262931882232b5f0af03cd4e908cf06",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-SECTOR-V1",
        "uuid": "48a57419-4118-45bc-88cb-87f6d2957c7b",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:VECTORADD_ORIGINAL4M",
        "arm": "SECTOR",
        "input_digest": "3375b4a8feb883fc39f2a7777d224f921a1ecd9ff3d624654a0c69efab0a0d09",
        "model": {
          "pid": 1289509,
          "requested_start_ticks": 969763228,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-3375b4a8feb883fc-SECTOR-V1.RESULT.json",
        "launcher": {
          "pid": 1289504,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 15625,
          "instructions": 56000000,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "9356cc250ad8842209bda580f3aeb4dc99dcd98a390217cf396f0499458bac86",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-BASE-V1",
        "uuid": "ef2a1a54-204d-4860-b2ef-39a2b0daf87b",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:M4_MIXED_AUTHORED",
        "arm": "BASE",
        "input_digest": "a24dde1bad963516ca1bb24a809c5c624e0c18ed216bc75711e3ebe20630cc6b",
        "model": {
          "pid": 1289430,
          "requested_start_ticks": 969763109,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-a24dde1bad963516-BASE-V1.RESULT.json",
        "launcher": {
          "pid": 1289425,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1,
          "instructions": 288,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "40aa9dc5d3108a658df06d7e3bc33037dc6c5bf458172c97df4280e7ea9fcda4",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-IO-V1",
        "uuid": "c44b2f93-fdc6-4d72-8aba-c6f4c641e977",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:M4_MIXED_AUTHORED",
        "arm": "IO",
        "input_digest": "a24dde1bad963516ca1bb24a809c5c624e0c18ed216bc75711e3ebe20630cc6b",
        "model": {
          "pid": 1289436,
          "requested_start_ticks": 969763121,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-a24dde1bad963516-IO-V1.RESULT.json",
        "launcher": {
          "pid": 1289431,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1,
          "instructions": 288,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "b0f43251c369495e80676005cc31bc22d5c0f84283bfdeecfd2ddec78c1d9a15",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-LEGACY-V1",
        "uuid": "72241a30-adc0-4aa5-9630-5750ad472e65",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:M4_MIXED_AUTHORED",
        "arm": "LEGACY",
        "input_digest": "a24dde1bad963516ca1bb24a809c5c624e0c18ed216bc75711e3ebe20630cc6b",
        "model": {
          "pid": 1289442,
          "requested_start_ticks": 969763132,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-a24dde1bad963516-LEGACY-V1.RESULT.json",
        "launcher": {
          "pid": 1289437,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1,
          "instructions": 288,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "13e40d383c18cb288fb4efcb2cb091fb4a0cce066b234dce403ae63413be47ae",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-OO-V1",
        "uuid": "86c5d8e7-3028-4bc1-9220-b700c8dd209f",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:M4_MIXED_AUTHORED",
        "arm": "OO",
        "input_digest": "a24dde1bad963516ca1bb24a809c5c624e0c18ed216bc75711e3ebe20630cc6b",
        "model": {
          "pid": 1289450,
          "requested_start_ticks": 969763143,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-a24dde1bad963516-OO-V1.RESULT.json",
        "launcher": {
          "pid": 1289445,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1,
          "instructions": 288,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "98557241018d26f6446c90b435a30947b1885ed54f5c613028a3bb16291907c8",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-SECTOR-V1",
        "uuid": "4d018c6b-bb75-4217-9382-4b098958d096",
        "program": "COMPONENT_SENTINEL_NOT_FORMAL:M4_MIXED_AUTHORED",
        "arm": "SECTOR",
        "input_digest": "a24dde1bad963516ca1bb24a809c5c624e0c18ed216bc75711e3ebe20630cc6b",
        "model": {
          "pid": 1289458,
          "requested_start_ticks": 969763153,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-SENT-a24dde1bad963516-SECTOR-V1.RESULT.json",
        "launcher": {
          "pid": 1289452,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1,
          "instructions": 288,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "44e6ceb4c8318dff3d4f4ce7ca1b5554d22556a240dc8b295db18229a87972b5",
        "category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "preserved_R14_canonical_category": "NATIVE_NATURAL_RECEIPT_AWAITING_STRICT_OR_ARCHIVE",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-ddb6806316876a85-CH-V1",
        "uuid": "520eccae-e73a-4e37-a480-6413a65e39bf",
        "program": "lavamd",
        "arm": "CH",
        "input_digest": "ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8",
        "model": {
          "pid": 1289743,
          "requested_start_ticks": 969764907,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-ddb6806316876a85-CH-V1.RESULT.json",
        "launcher": {
          "pid": 1289738,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1000,
          "instructions": 10396775488,
          "kernels": 1
        },
        "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
        "launcher_wait_returncode": 1,
        "DONE_sha256": "3d54409fc4f4bf588db38b32ba628329d39e59ee436b0697c37cc4b5689d8128",
        "category": "NATIVE_FAILURE_UNACCEPTED",
        "preserved_R14_canonical_category": "NATIVE_FAILURE_UNACCEPTED",
        "effective_V2_closed_category": "NATIVE_FAILURE_UNACCEPTED"
      },
      {
        "cohort": "E2-AEREPAIR-ddb6806316876a85-CM-V1",
        "uuid": "615d93c5-a990-4714-932b-9eac0b3ae6c9",
        "program": "lavamd",
        "arm": "CM",
        "input_digest": "ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8",
        "model": {
          "pid": 1289749,
          "requested_start_ticks": 969764919,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-ddb6806316876a85-CM-V1.RESULT.json",
        "launcher": {
          "pid": 1289744,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1000,
          "instructions": 10396775488,
          "kernels": 1
        },
        "recorded_stop_reason": "DTC_NATURAL_TELEMETRY_CLOSURE_MISSING",
        "launcher_wait_returncode": 1,
        "DONE_sha256": "81029d6f23ff4ffd41c47a118e38448c37e2d64f8c3e96811e92efb50ecee8c3",
        "category": "NATIVE_FAILURE_UNACCEPTED",
        "preserved_R14_canonical_category": "NATIVE_FAILURE_UNACCEPTED",
        "effective_V2_closed_category": "NATIVE_FAILURE_UNACCEPTED"
      },
      {
        "cohort": "E2-AEREPAIR-e7bb67e63e3c3847-DH-V1",
        "uuid": "63d903e5-df12-4331-a9f2-333f40bb9cee",
        "program": "vectorAdd",
        "arm": "DH",
        "input_digest": "e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799",
        "model": {
          "pid": 1289520,
          "requested_start_ticks": 969763251,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-e7bb67e63e3c3847-DH-V1.RESULT.json",
        "launcher": {
          "pid": 1289515,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 23438,
          "instructions": 84000768,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "b57bf46d97f7840ca9766ba18ef277c7dbf988277936274a52848985c641e584",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      },
      {
        "cohort": "E2-AEREPAIR-e7c791ce2e4b09ee-DM-V1",
        "uuid": "a3223b4f-65ae-4021-be09-5458eaba4c7f",
        "program": "b+tree",
        "arm": "DM",
        "input_digest": "e7c791ce2e4b09eea844428fdf220e0d3f095783c022a60aa9186c6146ddd83c",
        "model": {
          "pid": 1289553,
          "requested_start_ticks": 969763289,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/E2-AEREPAIR-e7c791ce2e4b09ee-DM-V1.RESULT.json",
        "launcher": {
          "pid": 1289548,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 16000,
          "instructions": 444467849,
          "kernels": 2
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "adbd572a2873728c71e238ff5faac38be86c3af21d371f6b06b851172e4111c0",
        "category": "PASS",
        "preserved_R14_canonical_category": "PASS",
        "effective_V2_closed_category": "PASS_CORRECTNESS_VALIDATION_ONLY"
      }
    ],
    "not_started": [],
    "independent_V2_postprocess_counts": {
      "PASS_CORRECTNESS_ARCHIVED": 21,
      "FAIL_ARCHIVED": 2
    },
    "independent_V2_postprocess": [
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-IO-V1",
        "uuid": "2d592f9b-06b2-4389-b685-e01d5e7900e1",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-3375b4a8feb883fc-IO-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "65a1002e3a517e517ffec2f1e84a57d8d7ebea865940732145985c903adbae9f",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-1df9d5479504d9c7-DM-V1",
        "uuid": "7ff782f3-0828-433c-a2cf-39854086ca01",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-1df9d5479504d9c7-DM-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "6015c638f60f1557e323028ef5ad0e045ee8158263cd803438e856679f0e3fa6",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-2b93f70cd0666c51-DH-V1",
        "uuid": "8f591968-b326-41b0-b52f-14182e81e21b",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-2b93f70cd0666c51-DH-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "46ff8dce4bc676f6884a686f502cab7269ab414694d48963066b098c5d19319c",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-2c506bf13c81ff5d-DM-V1",
        "uuid": "5678a8d9-1347-41f6-af70-83e33b6aac99",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-2c506bf13c81ff5d-DM-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "7f65ced7ca6b46cd866dc8fe5a5c9a3407d7e9f87a444ccbaedb2d680cbab5f4",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-BASE-V1",
        "uuid": "ef2a1a54-204d-4860-b2ef-39a2b0daf87b",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-a24dde1bad963516-BASE-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "4adc0a247d5399648391bdf68f1a04812b47755ef70181d5e99ebb7a82f4dc01",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-e7bb67e63e3c3847-DH-V1",
        "uuid": "63d903e5-df12-4331-a9f2-333f40bb9cee",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-e7bb67e63e3c3847-DH-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "9171f36762fb574ce22d536c0be151db06507c5a101d6ff300b4a14a9aaf2daf",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-SECTOR-V1",
        "uuid": "4d018c6b-bb75-4217-9382-4b098958d096",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-a24dde1bad963516-SECTOR-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "6a0f56749f5a162ed6720cc51780a6ab6127380069bb58512d79a95ba2da15f4",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-85700545918390d7-DM-V1",
        "uuid": "9c527401-db72-4098-941c-92efc0189045",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-85700545918390d7-DM-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "a1c6bc66dbc75001518b14b251025e1c5a35a9ce10a7ff49ad5157083eb0bbd5",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-977e34578994c3d2-DM-V1",
        "uuid": "dea19059-ef8c-4ab8-86e1-d86b19b50b6b",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-977e34578994c3d2-DM-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "f7f04da51cb3a56fa8b64c144a23cc2cd9634c1a1291622edeac2132a59dd31f",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-ddb6806316876a85-CM-V1",
        "uuid": "615d93c5-a990-4714-932b-9eac0b3ae6c9",
        "state": "FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY",
        "failed": true,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-ddb6806316876a85-CM-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "355d64f0e3baf1a17335a503f9b9e324bd0eb98be1ec9f7101f028f9f3c23ae4",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-BASE-V1",
        "uuid": "4a19a751-da84-4d11-ae33-eb183e715256",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-3375b4a8feb883fc-BASE-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "399b0019e86ddd74390f4d5f542b9f30e922318050b77043053b6d5ac5b911ca",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-e7c791ce2e4b09ee-DM-V1",
        "uuid": "a3223b4f-65ae-4021-be09-5458eaba4c7f",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-e7c791ce2e4b09ee-DM-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "dae378ed330221a15a26898c3615834746bbf2e1bd3372960197738e7436416a",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-SECTOR-V1",
        "uuid": "48a57419-4118-45bc-88cb-87f6d2957c7b",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-3375b4a8feb883fc-SECTOR-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "469756e7bd36ccda6be8a4c4d53be8b26d6cbe02693629f9223cf67a38246a2a",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-977e34578994c3d2-CH-V1",
        "uuid": "c9eb2ddd-b7e9-4367-bbba-fd7096f01f7f",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-977e34578994c3d2-CH-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "c20d60822b56f572715844c5cdc290950a5dfaa70166d72004376195cf40989a",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-OO-V1",
        "uuid": "86c5d8e7-3028-4bc1-9220-b700c8dd209f",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-a24dde1bad963516-OO-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "3a7a452d54351475b105c1c76670ad88c01cbec40be5ba7b9eeb67d3230835c5",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-LEGACY-V1",
        "uuid": "cf9404f2-1e13-4cc3-8fca-ecf536d25a26",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-3375b4a8feb883fc-LEGACY-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "51d47a915456b87f1aaf84a05c8f1d0f017460addc7576e758a354b9c98b85f4",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-LEGACY-V1",
        "uuid": "72241a30-adc0-4aa5-9630-5750ad472e65",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-a24dde1bad963516-LEGACY-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "94fb40959d4b04374ba3023183d257e71a329e5a6e2d86e370e8199767e1ff34",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-ddb6806316876a85-CH-V1",
        "uuid": "520eccae-e73a-4e37-a480-6413a65e39bf",
        "state": "FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY",
        "failed": true,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-ddb6806316876a85-CH-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "8004f93b43c71db38323d0de6525685f07915d1c481852eb281ba0a06af40f30",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-1df9d5479504d9c7-DH-V1",
        "uuid": "9d86d6e0-7005-4314-9248-bf09cb6e6fcc",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-1df9d5479504d9c7-DH-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "4fac2a7417a7f95dd31a9df52c9aa0513f8fdea7ba580489dacfec15d96c1136",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-09f94fcc7494a03b-DM-V1",
        "uuid": "ea54ebef-1873-4c57-9863-6629c1aa0305",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-09f94fcc7494a03b-DM-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "029bb53ab6231edcf64a9d0a85f8ee27e7f2eb3ac20c83f5e6d6a715f4336ea0",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-a24dde1bad963516-IO-V1",
        "uuid": "c44b2f93-fdc6-4d72-8aba-c6f4c641e977",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-a24dde1bad963516-IO-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "afded4cfe3ff9115ed0793790f0383fc005821db3021a197be297e12bd101937",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-SENT-3375b4a8feb883fc-OO-V1",
        "uuid": "d8e529fb-c282-423e-880f-4d574cf7e1df",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-SENT-3375b4a8feb883fc-OO-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "e8890793d91ed1e6150dd05657e880785bfaed62837b3f4896339e994808c440",
        "archive_restore_verified": true
      },
      {
        "cohort": "E2-AEREPAIR-09f94fcc7494a03b-DH-V1",
        "uuid": "864786c9-7e43-49d9-8c5b-8e008d980cfd",
        "state": "PASS_REPAIR_CORRECTNESS_V2_STRICT_ARCHIVE_RESTORE",
        "failed": false,
        "path": "/root/data/dtc_failure_repair_20261025_v1/validation/analysis/postprocess_v2/E2-AEREPAIR-09f94fcc7494a03b-DH-V1.POSTPROCESS_V2.RESULT.json",
        "sha256": "184982c2d963f389fcd19ab13cad4ad29c0d83d1a26aa7fb9c50bb5c1ac0d709",
        "archive_restore_verified": true
      }
    ],
    "V2_note": "All23 independently closed21correctnessPASS+2archivedFAIL;10 old sentinel ENGINEERING canonical files deliberately preserved and are not still awaiting simulation/strict.",
    "never_merge_with_original288": true,
    "accepted_original_performance_points_added": 0
  },
  "DTC_AE_LAVAMEM_REPAIR_20261026_V2": {
    "root": "/root/data/dtc_failure_repair_20261025_v1/validation_lava_memory_v2",
    "registered_budget": 2,
    "remaining": 1,
    "consumed": 1,
    "registry_state": "RUNNING",
    "registry_validation_status": null,
    "point_counts": {
      "PASS": 1
    },
    "preserved_R14_canonical_counts": null,
    "points": [
      {
        "cohort": "E2-AEREPAIR-LAVAMEM2-ddb6806316876a85-CH-V1",
        "uuid": "fa872b57-d23b-4654-840a-dd307476d0bb",
        "program": "lavamd",
        "arm": "CH",
        "input_digest": "ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8",
        "model": {
          "pid": 1344793,
          "requested_start_ticks": 971644356,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation_lava_memory_v2/analysis/E2-AEREPAIR-LAVAMEM2-ddb6806316876a85-CH-V1.RESULT.json",
        "launcher": {
          "pid": 1344788,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 1000,
          "instructions": 10396775488,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "c8d6e87468c729b5f0d07642fca0b279d034efdc7873d74ea67c70ea42591904",
        "category": "PASS"
      }
    ],
    "not_started": [
      "E2-AEREPAIR-LAVAMEM2-ddb6806316876a85-CM-V1"
    ],
    "independent_V2_postprocess_counts": {},
    "independent_V2_postprocess": [],
    "V2_note": null,
    "never_merge_with_original288": true,
    "accepted_original_performance_points_added": 0
  },
  "DTC_AE_LATE_FAILURE_REPAIR_20261026_V1": {
    "root": "/root/data/dtc_failure_repair_20261025_v1/validation_late_failure_v1",
    "registered_budget": 4,
    "remaining": 0,
    "consumed": 4,
    "registry_state": "RUNNING",
    "registry_validation_status": null,
    "point_counts": {
      "PASS": 3,
      "LIVE": 1
    },
    "preserved_R14_canonical_counts": null,
    "points": [
      {
        "cohort": "E2-AEREPAIR-LATE4-2b93f70cd0666c51-CM-V1",
        "uuid": "7b427c0f-c53b-4006-a5e0-5cebf2cf8945",
        "program": "scalarProd",
        "arm": "CM",
        "input_digest": "2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954",
        "model": {
          "pid": 1314581,
          "requested_start_ticks": 970418504,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation_late_failure_v1/analysis/E2-AEREPAIR-LATE4-2b93f70cd0666c51-CM-V1.RESULT.json",
        "launcher": {
          "pid": 1314576,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 128,
          "instructions": 730610912,
          "kernels": 1
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "e3cdbc40ff0ffa661052b75c7b82bb5bfbd2684e2161ee06dd02eae2b99766e3",
        "category": "PASS"
      },
      {
        "cohort": "E2-AEREPAIR-LATE4-769e6d9fd5f9cd53-CH-V1",
        "uuid": "a38e25bf-543f-4523-949c-9ab7757df2a2",
        "program": "GESUMMV",
        "arm": "CH",
        "input_digest": "769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4",
        "model": {
          "pid": 1314575,
          "start_ticks": 970418475,
          "state": "R",
          "same_generation": true,
          "alive": true,
          "actual_CPU_affinity": [
            144
          ]
        },
        "DONE_exists": false,
        "NATIVE_EXIT_exists": false,
        "registry_execution_receipt_exists": false,
        "result_state": null,
        "result_path": null,
        "launcher": {
          "pid": 1314570,
          "start_ticks": 970418474,
          "state": "S",
          "same_generation": true,
          "alive": true
        },
        "expected": {
          "CTA": 16,
          "instructions": 190918656,
          "kernels": 1
        },
        "category": "LIVE"
      },
      {
        "cohort": "E2-AEREPAIR-LATE4-e9110566572e0e0d-DH-V1",
        "uuid": "2ddd5860-134d-448e-92bc-1db8d5ac151c",
        "program": "hybridsort",
        "arm": "DH",
        "input_digest": "e9110566572e0e0dd3c00afc3aba533fa14ca3bb53a52cb44ffb4262b67be967",
        "model": {
          "pid": 1314595,
          "requested_start_ticks": 970418537,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation_late_failure_v1/analysis/E2-AEREPAIR-LATE4-e9110566572e0e0d-DH-V1.RESULT.json",
        "launcher": {
          "pid": 1314590,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 18260,
          "instructions": 623276352,
          "kernels": 56
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "093ef1858fe3e457a208c9bdfc1e62b6a9c5a57fe65f15495d7edb84e156696a",
        "category": "PASS"
      },
      {
        "cohort": "E2-AEREPAIR-LATE4-e9110566572e0e0d-DM-V1",
        "uuid": "acf185c4-17a7-47eb-9711-8150666c3534",
        "program": "hybridsort",
        "arm": "DM",
        "input_digest": "e9110566572e0e0dd3c00afc3aba533fa14ca3bb53a52cb44ffb4262b67be967",
        "model": {
          "pid": 1314589,
          "requested_start_ticks": 970418533,
          "alive": false,
          "proc_absent": true
        },
        "DONE_exists": true,
        "NATIVE_EXIT_exists": true,
        "registry_execution_receipt_exists": true,
        "result_state": "PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE",
        "result_path": "/root/data/dtc_failure_repair_20261025_v1/validation_late_failure_v1/analysis/E2-AEREPAIR-LATE4-e9110566572e0e0d-DM-V1.RESULT.json",
        "launcher": {
          "pid": 1314584,
          "requested_start_ticks": null,
          "alive": false,
          "proc_absent": true
        },
        "expected": {
          "CTA": 18260,
          "instructions": 623276352,
          "kernels": 56
        },
        "recorded_stop_reason": null,
        "launcher_wait_returncode": 0,
        "DONE_sha256": "c1cd3b2cd8fb228020b6e3ad95a4bc38eb22da83220b747cab1ccead45493036",
        "category": "PASS"
      }
    ],
    "not_started": [],
    "independent_V2_postprocess_counts": {},
    "independent_V2_postprocess": [],
    "V2_note": null,
    "never_merge_with_original288": true,
    "accepted_original_performance_points_added": 0
  }
}
```

### ETA

```json
{
  "source_path": "/root/data/dtc_failure_repair_20261025_v1/analysis/ETA_EVIDENCE_20261026T011933Z.json",
  "source_sha256": "ec55cbc6d46ef7fac78ca83ef79a39669bb34311da4d64705060338ad24e63d0",
  "source_checked_CST": "2026-10-26T09:19:32.539568+08:00",
  "method": "remaining instructions / recent observed30min or60min instruction rate, from authenticated same-generation progress; ordinary single point is pinned to one host CPU core.",
  "linear_extrapolation_only": true,
  "rows": [
    {
      "cohort": "E2-AEV100-1213f9ab49665a65-CH",
      "program": "kmeans",
      "uuid": "1c982147-a201-43f4-813c-7307ddc124fb",
      "pid": 1292091,
      "elapsed_h": 8.674841080604168,
      "completed": 89726240,
      "expected_instructions": 2165609728,
      "fraction": 0.04143232219540528,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.528113962,
          "instructions_per_second": 2243.217403094236,
          "prior_completed": 85687264
        },
        "3600": {
          "window_seconds": 3601.033069152,
          "instructions_per_second": 2380.97008146028,
          "prior_completed": 81152288
        }
      },
      "remaining_h_1800_3600": {
        "1800": 257.05680663266423,
        "3600": 242.18460648130647
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-CH",
      "program": "kmeans",
      "uuid": "97f34f82-2c2e-4c1d-8092-6ad1fa149126",
      "pid": 1264276,
      "elapsed_h": 11.117473530563611,
      "completed": 88226976,
      "expected_instructions": 1305753912,
      "fraction": 0.06756784351874107,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.644322833,
          "instructions_per_second": 1198.0778061743174,
          "prior_completed": 86069664
        },
        "3600": {
          "window_seconds": 3601.152432289,
          "instructions_per_second": 1352.2693336545756,
          "prior_completed": 83357248
        }
      },
      "remaining_h_1800_3600": {
        "1800": 282.28711434577656,
        "3600": 250.0995313948731
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-CM",
      "program": "kmeans",
      "uuid": "d72700d7-cc77-411f-af13-a3653df8170d",
      "pid": 1361316,
      "elapsed_h": 0.8170440322638889,
      "completed": 17069088,
      "expected_instructions": 1305753912,
      "fraction": 0.013072208969188981,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.571139965,
          "instructions_per_second": 4240.965452855384,
          "prior_completed": 9432928
        },
        "3600": {
          "window_seconds": 2941.35851615,
          "instructions_per_second": 5803.130732373983,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 84.40719705124023,
        "3600": 61.685325245158964
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-DH",
      "program": "kmeans",
      "uuid": "b52d5c8c-27a2-48d3-a2c8-70fe4814d098",
      "pid": 1361466,
      "elapsed_h": 0.8032135155191666,
      "completed": 16474432,
      "expected_instructions": 1305753912,
      "fraction": 0.012616796969626847,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.705933345,
          "instructions_per_second": 5311.730151425815,
          "prior_completed": 6909568
        },
        "3600": {
          "window_seconds": 2891.568655869,
          "instructions_per_second": 5697.403022598804,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 67.42307660202883,
        "3600": 62.859023219587975
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-DM",
      "program": "kmeans",
      "uuid": "29cf62cb-5af3-4743-b221-472e8d6e80b2",
      "pid": 1362999,
      "elapsed_h": 0.6448169099002777,
      "completed": 13875776,
      "expected_instructions": 1305753912,
      "fraction": 0.010626639424534996,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.644228696,
          "instructions_per_second": 5435.299124629206,
          "prior_completed": 4088736
        },
        "3600": {
          "window_seconds": 2321.340875641,
          "instructions_per_second": 5977.48316311728,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 66.02305219075845,
        "3600": 60.034470693621074
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-79f8ab6241faeed6-CH",
      "program": "3DCONV",
      "uuid": "cb0e9736-e699-4a1a-b8b8-386f18a11698",
      "pid": 1359774,
      "elapsed_h": 0.917168594318889,
      "completed": 494038313,
      "expected_instructions": 823239400,
      "fraction": 0.6001150005697006,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1798.994781504,
          "instructions_per_second": 143101.03378108525,
          "prior_completed": 236600300
        },
        "3600": {
          "window_seconds": 3301.806939548,
          "instructions_per_second": 149626.65051144123,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 0.639022262611885,
        "3600": 0.6111527998275718
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-79f8ab6241faeed6-DH",
      "program": "3DCONV",
      "uuid": "68e9d9b1-2e63-4310-bc1b-1805fc3a9940",
      "pid": 1360633,
      "elapsed_h": 0.8683066786075,
      "completed": 388932000,
      "expected_instructions": 823239400,
      "fraction": 0.47244094488188976,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1803.832093832,
          "instructions_per_second": 120894.41791488064,
          "prior_completed": 170858769
        },
        "3600": {
          "window_seconds": 3125.904042987,
          "instructions_per_second": 124422.24542131202,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 0.9979033484357015,
        "3600": 0.9696091244450417
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-CM",
      "program": "SYRK",
      "uuid": "89539cb0-0a41-402a-b19d-ca3b266ef263",
      "pid": 1285886,
      "elapsed_h": 9.188994865256111,
      "completed": 182192480,
      "expected_instructions": 5626658816,
      "fraction": 0.03238022527364133,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.41287941,
          "instructions_per_second": 6799.542560488531,
          "prior_completed": 169950496
        },
        "3600": {
          "window_seconds": 3600.828739482,
          "instructions_per_second": 6947.1651694267,
          "prior_completed": 157176928
        }
      },
      "remaining_h_1800_3600": {
        "1800": 222.4196328717944,
        "3600": 217.6933645763317
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-DH",
      "program": "SYRK",
      "uuid": "369ccba9-9ad9-407f-916b-5925044bdd6a",
      "pid": 1287678,
      "elapsed_h": 8.976536634971666,
      "completed": 473086432,
      "expected_instructions": 5626658816,
      "fraction": 0.08407945949285722,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.778904251,
          "instructions_per_second": 8995.414129830428,
          "prior_completed": 456887680
        },
        "3600": {
          "window_seconds": 3601.568801922,
          "instructions_per_second": 9153.859835304625,
          "prior_completed": 440118176
        }
      },
      "remaining_h_1800_3600": {
        "1800": 159.14196542626888,
        "3600": 156.38735027635528
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-DM",
      "program": "SYRK",
      "uuid": "04864616-6e93-422e-bf42-a2137574c43d",
      "pid": 1262476,
      "elapsed_h": 11.296482016381388,
      "completed": 129566336,
      "expected_instructions": 5626658816,
      "fraction": 0.02302722454604221,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.450651002,
          "instructions_per_second": 3568.990905928952,
          "prior_completed": 123140544
        },
        "3600": {
          "window_seconds": 3600.908513364,
          "instructions_per_second": 3568.806025564514,
          "prior_completed": 116715392
        }
      },
      "remaining_h_1800_3600": {
        "1800": 427.8436604578254,
        "3600": 427.86582470303836
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-f7d6397ed7ffa266-DH",
      "program": "streamcluster",
      "uuid": "c8310119-44a7-44de-ae3b-bb8c4e5c684a",
      "pid": 1285471,
      "elapsed_h": 9.2451541105975,
      "completed": 185070682,
      "expected_instructions": 577714898,
      "fraction": 0.32034950568299175,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.965865983,
          "instructions_per_second": 2381.4415814366603,
          "prior_completed": 180781787
        },
        "3600": {
          "window_seconds": 3601.912485741,
          "instructions_per_second": 2592.7256803072464,
          "prior_completed": 175731911
        }
      },
      "remaining_h_1800_3600": {
        "1800": 45.79908179480937,
        "3600": 42.06686368951029
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-f7d6397ed7ffa266-DM",
      "program": "streamcluster",
      "uuid": "c4a7e61b-83b0-46e2-81e4-02034124f0f0",
      "pid": 1285479,
      "elapsed_h": 9.245116307128056,
      "completed": 188447974,
      "expected_instructions": 577714898,
      "fraction": 0.3261954549768249,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.961718238,
          "instructions_per_second": 2407.4831553010386,
          "prior_completed": 184112189
        },
        "3600": {
          "window_seconds": 3601.831772676,
          "instructions_per_second": 2543.6748794053547,
          "prior_completed": 179286085
        }
      },
      "remaining_h_1800_3600": {
        "1800": 44.91400111067039,
        "3600": 42.50924596793952
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-fc0705ae3721e999-CH",
      "program": "GEMM",
      "uuid": "df58f975-ac7a-4735-81de-3512ff585c67",
      "pid": 1355741,
      "elapsed_h": 1.3151448974780555,
      "completed": 411321280,
      "expected_instructions": 739246080,
      "fraction": 0.5564064404643174,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.837195139,
          "instructions_per_second": 74000.76384457058,
          "prior_completed": 278057952
        },
        "3600": {
          "window_seconds": 3601.479982399,
          "instructions_per_second": 76640.44819045185,
          "prior_completed": 135302240
        }
      },
      "remaining_h_1800_3600": {
        "1800": 1.2309362429494095,
        "3600": 1.1885397903188486
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-fc0705ae3721e999-DH",
      "program": "GEMM",
      "uuid": "2261440b-c603-454c-8698-6a2d3caaefe8",
      "pid": 1356945,
      "elapsed_h": 1.1596837982719443,
      "completed": 424064544,
      "expected_instructions": 739246080,
      "fraction": 0.5736446299451463,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.906569711,
          "instructions_per_second": 94259.97486768075,
          "prior_completed": 254311136
        },
        "3600": {
          "window_seconds": 3601.698891919,
          "instructions_per_second": 99168.71196572883,
          "prior_completed": 66888704
        }
      },
      "remaining_h_1800_3600": {
        "1800": 0.9288186930833289,
        "3600": 0.8828432368560231
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-fc0705ae3721e999-DM",
      "program": "GEMM",
      "uuid": "8547fd04-5869-406b-b3a8-d64949c8f9ef",
      "pid": 1359687,
      "elapsed_h": 0.923590393503611,
      "completed": 196802208,
      "expected_instructions": 739246080,
      "fraction": 0.2662201577044548,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.909497671,
          "instructions_per_second": 58898.488867527536,
          "prior_completed": 90731360
        },
        "3600": {
          "window_seconds": 3324.925416613,
          "instructions_per_second": 59189.96168054693,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 2.5582804623771427,
        "3600": 2.5456825626372166
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-ffc8a89493c8a211-CM",
      "program": "sgemm",
      "uuid": "a508d776-1d32-4871-aee3-07ceb7be3015",
      "pid": 1365576,
      "elapsed_h": 0.3126905328213889,
      "completed": 936444448,
      "expected_instructions": 1658916864,
      "fraction": 0.5644914873805273,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1125.685918157,
          "instructions_per_second": 831887.8586783508,
          "prior_completed": 0
        },
        "3600": {
          "window_seconds": 1125.685918157,
          "instructions_per_second": 831887.8586783508,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 0.24124259072738516,
        "3600": 0.24124259072738516
      },
      "is_current_same_generation_live": false
    }
  ],
  "longest_examples": [
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-DM",
      "program": "SYRK",
      "uuid": "04864616-6e93-422e-bf42-a2137574c43d",
      "pid": 1262476,
      "elapsed_h": 11.296482016381388,
      "completed": 129566336,
      "expected_instructions": 5626658816,
      "fraction": 0.02302722454604221,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.450651002,
          "instructions_per_second": 3568.990905928952,
          "prior_completed": 123140544
        },
        "3600": {
          "window_seconds": 3600.908513364,
          "instructions_per_second": 3568.806025564514,
          "prior_completed": 116715392
        }
      },
      "remaining_h_1800_3600": {
        "1800": 427.8436604578254,
        "3600": 427.86582470303836
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-CH",
      "program": "kmeans",
      "uuid": "97f34f82-2c2e-4c1d-8092-6ad1fa149126",
      "pid": 1264276,
      "elapsed_h": 11.117473530563611,
      "completed": 88226976,
      "expected_instructions": 1305753912,
      "fraction": 0.06756784351874107,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.644322833,
          "instructions_per_second": 1198.0778061743174,
          "prior_completed": 86069664
        },
        "3600": {
          "window_seconds": 3601.152432289,
          "instructions_per_second": 1352.2693336545756,
          "prior_completed": 83357248
        }
      },
      "remaining_h_1800_3600": {
        "1800": 282.28711434577656,
        "3600": 250.0995313948731
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-1213f9ab49665a65-CH",
      "program": "kmeans",
      "uuid": "1c982147-a201-43f4-813c-7307ddc124fb",
      "pid": 1292091,
      "elapsed_h": 8.674841080604168,
      "completed": 89726240,
      "expected_instructions": 2165609728,
      "fraction": 0.04143232219540528,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.528113962,
          "instructions_per_second": 2243.217403094236,
          "prior_completed": 85687264
        },
        "3600": {
          "window_seconds": 3601.033069152,
          "instructions_per_second": 2380.97008146028,
          "prior_completed": 81152288
        }
      },
      "remaining_h_1800_3600": {
        "1800": 257.05680663266423,
        "3600": 242.18460648130647
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-CM",
      "program": "SYRK",
      "uuid": "89539cb0-0a41-402a-b19d-ca3b266ef263",
      "pid": 1285886,
      "elapsed_h": 9.188994865256111,
      "completed": 182192480,
      "expected_instructions": 5626658816,
      "fraction": 0.03238022527364133,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.41287941,
          "instructions_per_second": 6799.542560488531,
          "prior_completed": 169950496
        },
        "3600": {
          "window_seconds": 3600.828739482,
          "instructions_per_second": 6947.1651694267,
          "prior_completed": 157176928
        }
      },
      "remaining_h_1800_3600": {
        "1800": 222.4196328717944,
        "3600": 217.6933645763317
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-b51811aca9dc70cf-DH",
      "program": "SYRK",
      "uuid": "369ccba9-9ad9-407f-916b-5925044bdd6a",
      "pid": 1287678,
      "elapsed_h": 8.976536634971666,
      "completed": 473086432,
      "expected_instructions": 5626658816,
      "fraction": 0.08407945949285722,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.778904251,
          "instructions_per_second": 8995.414129830428,
          "prior_completed": 456887680
        },
        "3600": {
          "window_seconds": 3601.568801922,
          "instructions_per_second": 9153.859835304625,
          "prior_completed": 440118176
        }
      },
      "remaining_h_1800_3600": {
        "1800": 159.14196542626888,
        "3600": 156.38735027635528
      },
      "is_current_same_generation_live": true
    },
    {
      "cohort": "E2-AEV100-2315d0e612ee7cd4-CM",
      "program": "kmeans",
      "uuid": "d72700d7-cc77-411f-af13-a3653df8170d",
      "pid": 1361316,
      "elapsed_h": 0.8170440322638889,
      "completed": 17069088,
      "expected_instructions": 1305753912,
      "fraction": 0.013072208969188981,
      "rates_1800_3600": {
        "1800": {
          "window_seconds": 1800.571139965,
          "instructions_per_second": 4240.965452855384,
          "prior_completed": 9432928
        },
        "3600": {
          "window_seconds": 2941.35851615,
          "instructions_per_second": 5803.130732373983,
          "prior_completed": 0
        }
      },
      "remaining_h_1800_3600": {
        "1800": 84.40719705124023,
        "3600": 61.685325245158964
      },
      "is_current_same_generation_live": true
    }
  ],
  "not_a_completion_or_acceptance_guarantee": true,
  "calendar_statement": "No guarantee that all workloads, repair correctness and scientific acceptance finish during2026-11-13..2026-11-23; slowest phases, unstarted cells, source gates, failures and archive/native-restore replay remain.",
  "historical_repair_4_to_8_hours_prediction": "Historical estimate under the former R17 large-workload-first ordering, not a current promise. The prepared R18 short-first policy may postpone the remaining large LAVA admission and changes that ordering."
}
```

### storage

```json
{
  "recent_scoped_audit_path": "/root/data/dtc_failure_repair_20261025_v1/analysis/DTC_SCOPED_NATIVE_STORAGE_AUDIT_20261026T005126Z_V2.json",
  "recent_scoped_audit_UTC": "2026-10-26T00:51:26.723403+00:00",
  "recent_T_N_allocated_GiB": 2.217060089111328,
  "recent_DTC_roots_total_approx_GiB": 3.41,
  "recent_total_scope": "Prior root/parallel audit around08:58 CST: T+N+FIX+seven historical DTC roots; sharedtrace aliases/catalog reported separately; not a whole-host growth attribution.",
  "fresh_three_roots_measurement_UTC": "2026-10-26T01:47:48.498724+00:00",
  "fresh_three_roots_allocated_bytes": {
    "/root/data/dtc_main_v100_sweep_20261025_v1": 1827442688,
    "/root/data/ep_l2_dtc_l1_native_v2": 579366912,
    "/root/data/dtc_failure_repair_20261025_v1": 839843840
  },
  "fresh_three_roots_total_GiB": 3.023681640625,
  "historical_other_seven_DTC_roots_GiB": 0.4284325,
  "fresh_three_plus_previous_other_seven_approx_GiB": 3.452114140625,
  "mixed_time_sum_note": "Approximately3.45GiB; current three-root measurement plus earlier seven-root figure, not a new synchronous all-root inventory. Logs/request_history/publisher/metadata may all change; no attribution of the small difference without classification.",
  "T_net_growth_same_path_audit_GiB": 0.7297515869140625,
  "T_growth_baseline_UTC": "2026-10-25T10:06:56+00:00",
  "T_growth_cutoff_UTC": "2026-10-26T00:51:26.723403+00:00",
  "archive_SOURCE_KEEP_native_source_GiB": 0.675079345703125,
  "archive_native_restore_copy_GiB": 0.6734809875488281,
  "these_are_receipt_indexed_cold_candidates_not_deleted": true,
  "available_174_bytes": 39307931648,
  "available_174_GiB": 36.60836410522461,
  "genuine164_mount": {
    "filesystems": [
      {
        "target": "/root/share/mnt164",
        "source": "admin-wcx@10.208.130.164:/home/shared",
        "fstype": "fuse.sshfs"
      }
    ]
  },
  "no_unrelated15GiB_attribution": true
}
```

### open_items

```json
[
  {
    "id": "ORIGINAL16FAIL_3HOLES",
    "status": "OPEN_FOR_SCIENTIFIC_COMPLETENESS",
    "detail": "16 original native failures remain unaccepted, including independently closed GESUMMV;3 missing observer receipts remain charged and unaccepted. Repair correctness does not overwrite original performance evidence."
  },
  {
    "id": "LAVAMD_ORIGINAL_DH_NEW_FAILURE",
    "status": "DIAGNOSED_NO_ADDITIONAL_VALIDATION_SCOPE_REGISTERED",
    "cohort": "E2-AEV100-ddb6806316876a85-DH",
    "uuid": "545822b7-d775-4525-ace4-16825c3ea25b",
    "diagnosis_path": "/root/data/dtc_failure_repair_20261025_v1/analysis/NEW_ORIGINAL_LAVAMD_DH_DIAGNOSIS_20261026T003619Z.json",
    "diagnosis_sha256": "598521c4851b3af2f0d1789475e4046e8621bece1a183ac7dc3c177b949adf35",
    "detail": "Existing LAVAMEM2 finite scope covers CM/CH, not this newly failed original DH; no new repair attempt for DH is claimed."
  },
  {
    "id": "CUTCP4_ADMISSION",
    "status": "PREPARED_NOT_REGISTERED_NOT_STARTED",
    "candidate_path": "/root/data/dtc_main_v100_sweep_20261025_v1/control/CUTCP_FORMAT_ADMISSION_CANDIDATE.json",
    "cohorts": [
      "E2-AEV100-af7320f9d9dc6629-DM",
      "E2-AEV100-af7320f9d9dc6629-DH",
      "E2-AEV100-af7320f9d9dc6629-CM",
      "E2-AEV100-af7320f9d9dc6629-CH"
    ],
    "detail": "Prepared source-format adjudication does not mean admitted or started;4 original never-spent cells still absent from admitted_specs."
  },
  {
    "id": "ORIGINAL_FINAL_CONSUMER_OLD_GATE",
    "status": "NOT_CLOSED",
    "consumer_path": "/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_final_consumer_v10.py",
    "source_top_gate_requires_original_q_state": "ALL_STARTS_CLOSED_PENDING_COMPLETE_SCIENTIFIC_DELIVERY",
    "source_top_gate_requires_remaining": 0,
    "actual_q_state": "RUNNING",
    "actual_remaining": 91,
    "COMPLETE_RESULT_exists": false,
    "waiter_state": {
      "state": "WAIT_NATIVE_MATRIX",
      "observed_utc": "2026-10-26T01:46:51.438127+00:00",
      "actual_pid": 1262421,
      "scientific_model_starts": 0,
      "scientific_authority_writes": 0,
      "consumed": 265,
      "remaining_registered": 91,
      "actual_controller_pids": [
        1112475
      ]
    },
    "detail": "Do not equate repaired points or native terminal evidence without receipts with passage of the original full-source consumer and domain/adjudication gates."
  }
]
```

### paper

```json
{
  "last_confirmed_mother": "English v0.23",
  "newer_mother_promoted": false,
  "performance_claim_limit": "Matched-cache-hash question and original complete four-cell comparisons still require final source/acceptance review; no completion-biased interim mean or unique DTC causality claim."
}
```

Facts source: analysis/current_state_review_20261026_v1/STATE_FACTS_V1.json

SHA256: 7edb637926ea34c967d46731aaaff33c02b8dbdc9b9aa4b8be3dbda0a6acd890

R18 total qualification SHA256: 72f111e38b0d000f29d223600a9b22333dc1df71d23b9f3848bf12111e8a2270
