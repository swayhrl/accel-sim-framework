# C16 V12.4 — TWO-HOUR LLAMA FINISH OR SHUTDOWN

## Frozen current facts

- Primary model remains `meta-llama/Llama-3.2-1B`, S0 / B1 / T128 / Decode4.
- Active GPU branch checkpoint observed at review start: `417316798c49eea2e9f3ab113f1dd358879b7048`.
- Route-B Q1 is PASS and has real dynamic nonzero GPU-VA evidence: 692 LANE_EVENT records, two exact launches, zero overflow/drop, COMPLETE terminal.
- Q2 bridge code is integrated; fresh-map width authority is closed.
- The old shared Recovery-V3 campaign ledger cannot admit new work because its historical SHA is unavailable on the node. A new Llama-primary campaign ledger is initialized from the stable live historical snapshot. The rebind receipt itself is provenance-only (`scientific_eligible=false`); future scientific artifacts must independently bind model/input/runtime/map/producer identities and may not use the rebind receipt as scientific evidence.
- Q2 Prefill and Decode have not yet produced accepted GPU dynamic captures at this checkpoint.
- Representative Route-B selection remains blocked by two failed-closed CUTLASS actual-owner rows.

## Time policy

This is a bounded rental-server sprint. Do not broaden scope.

From receipt of this handoff, spend at most two hours before shutdown/closeout decision.

Priority order:

1. Q2 Prefill dynamic capture.
2. Q2 Decode dynamic capture.
3. CUTLASS actual-owner closure only if needed for representative selection.
4. Freeze representative selection.
5. Route-B canary / formal capture if selection becomes admissible.
6. Route-C only if formal Route-B capture is already closed and time remains.

No Qwen/AWQ/Qwen3/DeepSeek/GLM work during this sprint.

## Escalation thresholds

- Ordinary engineering blocker: 15 minutes max before switching to smallest diagnostic that can decide the blocker.
- Same root cause may not consume more than 30 minutes without new direct evidence.
- CPU documentation/publication work must not delay a ready GPU action.

## 30-minute checkpoint

By +30 min, at least one of these must be true:

- Q2 Prefill PASS with remote SHA-closed raw dynamic address evidence; or
- a minimal, specific external blocker is documented with the exact failing command/receipt and a bounded next experiment already running.

If neither is true, enter shutdown-harvest mode instead of opening another research branch.

## 60-minute checkpoint

Target: both Q2 Prefill and Decode closed.

If both Q2 rows are PASS, immediately return to the two CUTLASS owner gaps and final selection.

If Q2 is still not closed after one hour, stop all nonessential debugging and ensure all current Q1/Q2/map evidence is retained and copyback-ready.

## 120-minute hard decision

At +120 min, either:

- Llama has materially advanced into representative Route-B capture; continue only if a GPU capture is actively producing useful scientific raw data; or
- enter final shutdown-harvest and stop spending rental time.

## Shutdown-harvest requirements

Before server shutdown/release:

1. No active measurement marker and no GPU process.
2. Commit/push compact receipts/status for every accepted result and every terminal failed-closed result.
3. Produce a single `LLAMA_RENTAL_SHUTDOWN_MANIFEST.json` containing for every critical raw artifact:
   - artifact role
   - remote path
   - byte size
   - SHA256
   - producing commit
   - run id
   - copyback state
4. Prioritize copyback of irreplaceable Llama artifacts only:
   - Q1 raw + parse manifest
   - Q2 Prefill raw/map/whitelist/parse manifest if produced
   - Q2 Decode raw/map/whitelist/parse manifest if produced
   - unresolved CUTLASS diagnostic receipts needed to resume later
   - final selection / Route-B formal raw if produced
5. Do not spend the final window copying historical Qwen/AWQ artifacts unless all Llama critical artifacts are safe.
6. Never delete the sole remote copy unless local SHA equality is verified.

## Acceptance semantics

Q1 qualification proves the new producer works on a controlled tiny CUDA fixture. It is not Llama scientific evidence.

Q2 is the first required new Llama dynamic producer qualification. Accept only if:

- exact Llama anchor function identity is closed;
- fresh actual-owner static map is closed;
- all GLOBAL+MREF rows/ordinals are frozen;
- raw LANE_EVENT stream has nonzero GPU VAs;
- COMPLETE terminal; overflow=0; drop=0; event_count matches parser;
- Route-A bridge structural comparison passes without requiring absolute VA equality across processes;
- raw bytes and all compact manifests are remote SHA-closed.

The new Llama-primary campaign ledger is an execution-control namespace. The ledger-rebind receipt being `scientific_eligible=false` must not be misrepresented as scientific validation of Q2/formal captures.