# A16B LATPC no-op variant slot guidance

## Goal

Create a paper-specific variant slot for LATPC.

The variant slot must be no-op. It must preserve baseline simulator behavior exactly.

## Inputs

A16A selected workload JSON:

.local_reports/A16A_latpc_selected_workload_*.json

Paper profile:

.local_reports/A16A_latpc_paper_profile_*.md

Existing scripts from A0-A15 under:

scripts/accelsim/

## Required tracked script or library

Create a small reusable library or config file under scripts/accelsim.

Recommended:

scripts/accelsim/a16_latpc_variant_lib.py

This library should define at least:

- load_latest_selected_workload()
- get_latpc_variants()
- build_variant_manifest()
- write_variant_manifest()

Variant definitions:

baseline:
  paper: LATPC
  variant_id: baseline
  behavior: baseline
  config_mode: original
  simulator_delta: none

latpc_noop:
  paper: LATPC
  variant_id: latpc_noop
  behavior: no-op
  config_mode: same_as_baseline
  simulator_delta: none
  purpose: validate baseline-vs-variant pipeline before LATPC mechanism implementation

## No-op requirements

latpc_noop must use:

- same simulator binary as baseline
- same kernelslist as baseline
- same config as baseline
- same simulator arguments as baseline
- same environment, except optional metadata variables that do not affect simulator behavior

Allowed metadata environment variables:

- ACCELSIM_PAPER=LATPC
- ACCELSIM_VARIANT=latpc_noop
- ACCELSIM_ROUND=A16

If any existing script would pass ACCELSIM_VARIANT into simulator config or alter behavior, do not use that path.

## Required implementation

Create or update a script:

scripts/accelsim/a16_latpc_variant_slot.py

The script should:

1. Read the latest A16A selected workload JSON.
2. Build a variant manifest containing baseline and latpc_noop.
3. Validate that baseline and latpc_noop have identical execution inputs.
4. Write the manifest JSON under .local_reports.
5. Write a short MD summary under .local_reports.
6. Record start time, end time, and wall seconds.

## Required output files

.local_reports/A16B_latpc_variant_manifest_<timestamp>.json
.local_reports/A16B_latpc_variant_slot_<timestamp>.md

## Manifest fields

Include at least:

- paper
- round
- selected_workload
- variants
- baseline
- latpc_noop
- kernelslist_path
- config_path
- simulator_delta
- noop_equivalence_expected
- status
- timestamp

For each variant include:

- variant_id
- variant_kind
- command_role
- kernelslist_path
- config_path
- simulator_binary
- simulator_args_signature
- semantic_delta
- expected_stats_relation_to_baseline

## A16B status rules

PASS:

- A16A selected workload JSON exists
- baseline and latpc_noop manifest entries exist
- no-op equivalence validation passes
- required reports exist

BLOCKED_NO_A16A:

- no selected workload JSON exists

FAIL_NOOP_NOT_EQUIVALENT:

- baseline and latpc_noop would use different simulator inputs

PASS_WITH_WARNINGS:

- manifest complete but simulator binary path has to be resolved later by runner

## Validation commands

Run:

python3 scripts/accelsim/a16_latpc_variant_slot.py

Then inspect:

ls -lh .local_reports/A16B_latpc_*
cat latest A16B summary
python3 -m json.tool latest A16B manifest

## Important notes

Do not patch Accel-Sim simulator source in A16B.

Do not create a fake LATPC config that changes simulator behavior.

Do not add a config flag that pretends LATPC exists.

This stage is only a clean variant slot and metadata layer.
