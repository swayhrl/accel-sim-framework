# Gate C native admission assessment (static; no model starts)

The isolated `first4_GESUMMV.static.json` and `FRONTEND_DRYRUN_MANIFEST.json` pin the four input rows, the actual new binary and libcudart hashes, and five config files per mode. The four copied DH-P0 base configs retain their original bytes; OFF and ON add only a new one-line candidate switch. This is a source/config dry-run, not launcher qualification.

## Existing native route cannot admit this Goal

- The historical Oracle `remaining24/control/NATIVE_ROUTE_BLOCK.sh` dispatches only its exact `E2-DTCORACLE-R24-*` cohort IDs. Its frontend requires the Oracle entry marker and Oracle execution plan.
- `remaining24/tools/oracle_native.py` requires the old Oracle request, cohort prefix, source/spec hashes and parent lease. Its registry mutator protects the Oracle request and peers. Its strict pipeline is tied to Oracle identity, result adapter and observer bindings.
- `remaining24/tools/oracle_ops.py` attaches only the historical initial8/remaining24 roots to an owner-pinned shared pool. It cannot accept this new Goal as a third context and is not a fresh dispatcher.
- The generic `sweep_native_cap1m.py` consumes a UUID by writing a fresh `INTENT.json` under the native registry lock, decrementing that request's remaining budget, and later attaching the execution receipt. That transaction shape is reusable as a design constraint; its old request and lease cannot be reused.

## Minimum trustworthy new route

1. Create a new exact four-cell request and frozen specs in this isolated Goal tree. An independent reviewer must check the new request ID, one-cell-one-budget accounting, source and runtime pins, candidate option pair equivalence, resource limits and guard before registration.
2. Under the native `REGISTRY_UPDATE.lock`, append a new request to `registered_future_requests` while preserving all historical entries byte-for-byte at the semantic level. Update the registry/epoch hash transactionally and verify global budget arithmetic. A policy requiring zero writes to the shared native registry is incompatible with native science admission.
3. Create one new dispatcher and parent lease for this request, with a bounded CPU/resource reservation. The new exact native route must reject every old Oracle ID and any unregistered new ID. A single consumption transaction must allocate a fresh one-use UUID and write the matching `INTENT.json` exactly once; uncertain/failed starts remain charged and are never retried under a reused identity.
4. Independently qualify actual child argv/cwd, PID/start, binary/lib/loader maps, config/options echo and runtime guard. A new mechanism strict verifier must accept only natural full-input completion with correct kernel/CTA/instruction counts, actual ON decision/exposure, and complete lifecycle semantics. Then close true164 SOURCE_KEEP and typed native restore.

None of steps 1-4 is satisfied by the static frontend files. Gate C science admission is HOLD; new scientific starts remain zero. The historical owner, registry entries, requests, UUIDs and publisher are untouched.
