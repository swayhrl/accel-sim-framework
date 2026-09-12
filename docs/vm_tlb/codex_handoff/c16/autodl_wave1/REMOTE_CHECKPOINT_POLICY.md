# C16 G Remote Checkpoint / Push Policy

Purpose: keep the active AutoDL runtime observable from GitHub without turning every run or diagnostic file into Git history. This policy does not authorize new scientific scenarios.

## Commit and push immediately at these boundaries

1. **Runtime implementation boundary before future scientific runs**
   - source code or contract logic used by a scientific run changes (runner, profiler wrapper, budget/measurement guard, package verifier, resident runner, catalog validator, schema).
   - run the relevant focused tests first; commit/push the clean source change before the next scientific run consumes it.
   - scientific receipts must bind the resulting exact commit.

2. **Qualification state transition**
   - G0/G1/G2/G3 changes from pending/diagnostic to PASS, CAPABILITY_LIMITED, or bounded NO_GO.
   - commit a small receipt/status summary plus hashes/paths of large raw artifacts; never commit raw profiler/trace blobs.

3. **Cross-lane consumable checkpoint**
   - early real-native canary checkpoint;
   - NATIVE_CATALOG_V1 or later catalog revision;
   - tiny NVBit real-trace canary manifest for H;
   - a newly consumed Lane-A rolling package (P2/P3/etc.) after transfer + hash closure.
   These must be pushed immediately so C/H/ChatGPT can review fixed remote evidence.

4. **Execution-path decision that changes future work**
   - resident-model GO/NO_GO;
   - scenario becomes SKIPPED_RESOURCE;
   - profiler/counter/NVBit capability gap changes the planned path;
   - package/revision/hash mismatch causes quarantine.
   Preserve the evidence boundary and push it before continuing on a different path.

5. **Before a long unattended GPU batch**
   - if the source tree has scientific-runtime changes not yet pushed, stop before the batch, test, commit, and push.
   - do not run many scenarios from an unpushed mutable runtime tree.

## Do NOT commit for these events alone

- every baseline repetition;
- every scenario if no state/contract changes and outputs are large raw files;
- transfer progress percentages;
- intermediate SQLite/TSV exports;
- retry logs or diagnostic stdout;
- large `.nsys-rep`, SQLite, NVBit raw, model weights.

Large artifacts remain outside Git and are represented by immutable path/size/SHA256/run identity in small manifests/receipts.

## Suggested commit grouping

- `runtime:` code/guard fix + focused tests;
- `qual:` G0/G1/G2/G3 state change;
- `data:` one logically complete model/scenario-group native checkpoint;
- `consume:` one A rolling package closure;
- `diag:` bounded NO_GO/capability result that changes the path.

Do not mix unrelated runtime-source changes and scientific output publication in one commit when they can be separated cleanly.

## Push rule

Every milestone commit above is pushed immediately to `hrl/vm-c16-g-autodl-wave1-v0`. Never force-push or rewrite an already referenced scientific commit. If the active tree is dirty because a measurement is running, wait for that measurement to close, then commit; never alter files participating in an active formal measurement.

## Status visibility

Maintain a compact `LATEST_RUNTIME_STATUS.md` or equivalent committed status at milestone boundaries containing only:
- current source/runtime commit;
- consumed A package IDs + commit + manifest SHA;
- latest qualified G0/G1/G2/G3 states;
- latest model/scenario group completed;
- next queued GPU task;
- large-artifact manifest/index references;
- known capability/no-go items.

This file is navigation metadata, not a substitute for the underlying receipts.