# Gate C first-four static route: source binding only

This directory holds a read-only route draft for the first four cells: `W OFF`, `W ON`, `vectorAdd OFF`, `vectorAdd ON`. It is not a science admission, execution request, UUID reservation, strict result, or archive.

Run `python3 first4_route.py --check-all` to verify all four contract-permitted witness choices without choosing W. The script verifies each fixed CORE32 input binding file hash, full input digest, kernel/CTA/instruction declaration, the historical DH-P0 spec hash and 270 base options. For each pair it adds only `-gpgpu_dtc_l1_short_collect_first`, producing 271 effective options. It verifies that OFF and ON differ only in that option. The historical Oracle OFF spec is cross-checked as provenance only; its Oracle bit, request, UUID, binary, strict result and performance result are not execution bindings for this Goal.

Main must freeze W from the approved Gate A evidence. Only after that may `python3 first4_route.py --witness W --output first4_W.static.json` write the four-row static draft within this directory. The draft deliberately leaves `request`, `uuid`, actual new binary and libcudart SHA, new config SHA, runtime guard, strict, true164 archive and typed native restore unbound.

## Required new route before any model launch

1. Freeze one exact four-cell scientific request under this Goal, check the pre-registered W and vectorAdd input bindings, and allocate a fresh one-use UUID per cell through the authorized sole dispatcher. Check no UUID or request aliases historical Oracle identities.
2. Bind each cell to the same actual new frozen binary, libcudart, framework source/build, complete effective config/options, and trace input. Check both modes use the new binary and actual OFF/ON switch; no old DH-P0 or Oracle OFF result can substitute for a run.
3. Provide a new strict verifier for this mechanism. It must prove true natural full-input completion and expected kernel/CTA/instruction counts; exact input, mode and options; actual PID/start/maps/loader/libs/argv/cwd and resource guard; candidate decision and positive exposure from ON events; OFF telemetry neutrality; lifecycle, credit/ref/waiter exactly-once and completion semantics. A config echo, sparse statistic, early exit or inherited Oracle strict PASS cannot satisfy this gate.
4. Archive each closed raw stream and all dependencies to true164 with chunk, whole-stream hash, COMMIT/index and SOURCE_KEEP checks. Perform typed native restore and compare restored files and strict evidence to the source. Reusing archive primitives is permissible; reusing old Oracle source identity or result is not.
5. Obtain independent safety and scientific review of all four accepted cells before registering the later 16. If no positive ON decision/exposure, failed strict, failed archive or review HOLD, stop without registering the remaining 16.

The current script completes only the source-pinned static portion. It does not close the request, execution, strict, archive or restore obligations.
