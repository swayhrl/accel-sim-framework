# Stage II-A first16 automatic read-only analysis

`readonly_analysis_service.py` is a single-writer **analysis service**, not a model controller. Its sole role is to read the already registered16 first-batch CH points and32 frozen original references, independently check evidence through frozen adapter V1, update matched result tables and expose a Root publication provider. It performs no registration, model dispatch/retry, owner signal, original-result edit, archive write, scientific acceptance write or Git action. The remaining48 stay locked.

Actual compatibility: registered budget16, exact eight input identities, fixed plan5001c3f and `remaining48_not_authorized=true`. The current results/strict schemas match adapter V1; outbox6c4dca retains the same receipt/manifest/native-restore shape. The adapter dynamically checks registered engine/strict/outbox and EXECUTION_PLAN pins before accepting any result.

A standalone background analysis process is already running. See OWNER.json and BACKGROUND_ANALYSIS_START_RECEIPT.json for PID/start/source binding. Flock prevents a second analysis writer. Native dispatch and Root's strict/archive producer remain the existing sole scientific execution/result owners.

## CLI

- `python3 -B readonly_analysis_service.py --status`: inspect HEALTH/LATEST only.
- `python3 -B readonly_analysis_service.py --once`: one read/update if no background analysis owner holds the lock; otherwise reports existing owner and exits.
- `python3 -u -B readonly_analysis_service.py --watch --interval-seconds 120 --full-audit-seconds 1800`: the existing background mode; do not launch another copy while OWNER is live.

Poll default: every120seconds hash the16 RESULT/INTENT/DONE/archive-receipt inputs. Unchanged inputs do not generate snapshots or reread full archives. A changed/new terminal RESULT or a verification HOLD triggers analysis; HOLD retries on the next120-second poll. Every1800seconds a full archive chunk/stream and all native-restored-file audit is repeated. Between full audits an already qualified immutable point can reuse its full-archive validation only after all critical JSON witness SHA values still match; each row records full-audit time and validation mode. No source result is rewritten.

Output: immutable `snapshots/<UTC-and-signature>/` with OBSERVATIONS, RESULTS, SUMMARY, compressed copies and manifest. LATEST.json points to the latest analysis; PUBLICATION_PROVIDER.json binds four review files by SHA for **Root's unique publisher**. No publisher is started here. First8 subset GM, per-F denominators, common F128/F256 accepted set, positive/zero/negative/missing and source references remain explicit. No IR/R2/EP/PQ/PS performance substitution occurs.

The service exits normally after all registered16 are independently verified terminal (accepted or archived-negative), after writing final tables/provider. This does not imply all16 pass, full35 coverage, equal L1 hardware cost, or a successful remote publication; Root owns publication/readback. Its own STOP_ANALYSIS_REQUESTED file only stops this reader and never signals a model.

7 synthetic service checks pass (critical-witness cache invalidation, result-change signature, atomic owned-state output); the frozen consumer's18 CPU checks and frozen adapter's17 archive checks remain separate. The actual no-result registered-context smoke passed with4consumed/12remaining and16 missing rows. A first naturally completed accepted vectorAdd result is still required before declaring that real accepted path qualified. Raw printed cycles alone never qualify.
