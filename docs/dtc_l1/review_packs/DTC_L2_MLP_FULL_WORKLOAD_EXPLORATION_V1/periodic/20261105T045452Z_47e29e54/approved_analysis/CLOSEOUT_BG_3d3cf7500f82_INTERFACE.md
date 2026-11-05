# Fixed historical provider V2 candidate

Candidate only: no production daemon, simulator, controller, Goal, health model, publisher, Git, or READY action has been run by this package. V1 evidence is unchanged.

## Interface

Run Python with `-B` / `PYTHONDONTWRITEBYTECODE=1`. Import the exact SHA-pinned `historical_provider.py` with `importlib.util.spec_from_file_location` and call `collect(previous=None)`. Return value is a JSON-serializable dict with schema `HISTORICAL_LONGTAIL_PROVIDER_V2`. The function performs reads only: no writes, sleeping, subprocess, model discovery, network, controller action, or publishing. Caller owns scheduling, immutable per-epoch run storage and all publication. An optional previous value is the prior complete return object; only matching scope/PID/start/boot permits a CPU-tick delta. A single unchanged CPU sample does not prove a stall or stop.

`python3 -B historical_provider.py` prints one compact JSON object to stdout and exits. It does not persist it. No command line arguments or future experiment discovery are supported.

## Scope and identity

`SCOPE.json` fixes exactly these three observed UUID generations:

| Cohort | UUID | PID/start ticks |
|---|---|---|
| SYRK S REF | f406dae1-f20b-4356-aba2-13dee73f6401 | 2053685/989697704 |
| SYRK F REF | 1e3ed644-f904-4b09-856e-62d398dafdf6 | 2194211/994648903 |
| LAVAMD F REF | 56e7a936-1179-4466-8c2a-073df0e7a69c | 2224914/995749284 |

The scope also pins each request/cohort/output, boot, input identity, source Core/Framework/binary/archive identity, whole-work expectation, run FROZEN_SPEC, input binding, exact generation metadata and ordered configuration hashes. Changing scope requires a separately reviewed provider/source pin. No new experiment becomes observed when these objects close. The registry is read solely to resolve these exact cohort/UUID terminal receipts and the explicitly fixed LAVAMD S comparison baseline. Other lanes are neither followed nor aggregated.

## Output and completion

- `objects`: always the exact three fixed UUIDs when scope/registry reads succeed. Per object: `status`, `terminal`, `accepted`, `cycles`, process observation, configuration/source/input identity, evidence references and `baseline_comparison`. Read/schema/source errors stay HOLD; missing process handles and reused PIDs do not imply termination.
- `process`: fixed PID/start/boot, handle status, CPU ticks and optional CPU-tick delta. No replacement PID is searched. Progress includes raw compressed bytes and the prior initial telemetry cycle. No current completion fraction or ETA is invented.
- `completion.scope_object_count`: 3.
- `completion.terminal_object_count`: number whose status is exactly `STRICT_ACCEPTED` or `EXPLICIT_UNACCEPTED` with coherent own terminal evidence and no live/terminal conflict.
- `completion.all_fixed_objects_terminal`: true only if all three are terminal. Use this exact boolean for the historical observation completion decision; HOLD and handle loss never complete the scope.
- `signature`: scientific state SHA256. UTC, process tick totals/deltas, elapsed time, raw file growth and unrelated registry SHA are excluded. LIVE_CPU_PROGRESS and LIVE_SAME_GENERATION normalize to the same signature. Terminal acceptance/cycles/source/input/comparison changes produce a new signature.

Strict positive requires existing own DONE/EXIT, exact fixed UUID/spec/source/generation, registry CLOSED_ACCEPTED with all linked SHA references, application accepted point, validated bundle with exact work/options/input/source and matching positive cycles, complete untruncated raw stream receipt, and existing archive receipt with FIRST plus INDEPENDENT successful restore records. This observer consumes those existing authority receipts; it does not rerun scientific validation or perform a new archive/restore. `numeric_output` is preserved as reported, including UNKNOWN.

Explicit negative requires coherent own DONE/EXIT with nonzero native return code/stop reason, or exact closed-unaccepted registry plus archive receipt without an accepted point. It returns no accepted cycles. Positive/negative and live/terminal conflicts remain HOLD. A native rc0 without mandatory strict/archive closure remains HOLD_DONE_PENDING_STRICT_ACCEPTANCE.

## Baselines and role isolation

`DOWNSTREAM18_BASELINE.json` contains the immutable 18 strict accepted points and source SHA references. Each CH/DH lane normalizes against its own P0=1. Source hashes are reread every collection; any changed source suppresses the table. PQ changes only partition queues 64:64:64:64 to 64:256:64:64; PS changes only DRAM clock from 850 to1700 MHz (other clocks1410 MHz). This is NEW_DOWNSTREAM18_ONLY, never original288, repair validation, current DTC-L2 or EP.

For EP, SYRK S is its own baseline after strict acceptance; SYRK F uses this exact SYRK S UUID. LAVAMD F uses only the fixed preexisting LAVAMD S UUID f293d9bc-a02c-4bb0-a213-1793294fb13d. Ratios appear only if both explicit same-input/source/whole-work/clock points are strictly accepted. All configuration differences are displayed. No cross-input, DTC/EP or cross-lane geometric mean is computed.

Old V100 is static historical context via the SHA-pinned V1 report: no simulator at that snapshot; 284 starts, 281 receipts and 3 preserved unaccepted receipt gaps. Its registry RUNNING and remaining72 are not live-tail counts, and its old planned full matrix is not certified complete. The provider does not read or manage its controllers.

## CPU qualification and payload

`qualify_provider.py` performs positive/negative/identity/partial-evidence/conflict/handle-loss/PID-reuse/contract/baseline/signature/size tests. Only this script writes its own CPU_QUALIFICATION.json and QUALIFICATION_SAMPLE.json. It starts no daemon or scientific model. The provider output is bounded below1MiB uncompressed (therefore also comfortably below the requested compressed budget in the qualified sample). K may compress and store it as an immutable historical subreport using its separately authorized READY ownership; this package has no READY or publisher code.
