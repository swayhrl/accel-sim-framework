# FWT / SGEMM resource and pipeline review

This is a read-only proposal, not application, native-test, build, qualification or budget authorization. No central registry, lease, controller, original status or other project was changed. `RESOURCE_COST_REVIEW.json` records the exact snapshot, registry hash, bounded collection and original-gate forecasts. `collect.py` only reads resources and writes that evidence file in this isolated directory.

At the recorded snapshot, original174 is `huangrulin-174`, original boot `59e1e1a4-84b6-431f-ac2d-03e340207019`. Actual count and recount are 46; T0 remains 1792414193, contingency remains fully consumed. The original controller is STOPPED; its process, final collector and native process are absent. The central registry has no RUNNING/RESERVED rows, and no simulator or E execution supervisor was found in the bounded PID inspection. This is a point-in-time observation, not a reservation or permission to create a controller.

Workspace available space is approximately 17.07 GiB and Share 41.18 GiB. Effective available RAM is approximately 199.44 GiB; cgroup RAM limit is 256 GiB, CPU quota 384 CPU units and affinity 512 logical CPUs. The original shared admission limits still apply: total reservation at most 8 CPU units and 32 GiB RAM, available RAM floor 64 GiB, Share floor 40 GiB, workspace floor 5 GiB plus the existing 2 GiB monitor reserve **per admitted endpoint**. Physical resources are not inferred from the historical fixed simulator-count fields. The applied RESOURCE_ONLY amendment means no added two-route or other fixed formal-simulation count cap.

The exact new-result root was inspected only through directory metadata: 408 directories, 2,233 regular files, 6,899,258,320 logical bytes, 6,904,942,592 allocated bytes; no raw or trace content was read. This matches the final ledger, with no measured new-root metadata growth since that ledger. Historical old generation remains 14,309,576,384 B without recounting, subtracting migrated files or resetting history. Conservative cumulative new/total generation is therefore 6,899,258,320 / 21,208,834,704 B. Remaining generation is 3,838,159,920 B under the 10 GiB new ceiling and 4,560,969,072 B under the 24 GiB total ceiling. Repository proposal metadata is outside that measured result root and still consumes actual workspace; any later collector/qualification/result metadata must be accounted at admission.

## Exact future budget proposal

Original 32-row research allocation and all original contingency usage stay byte-preserved. Removal of an overall numeric launch cap does not make those exhausted buckets reusable. Request two explicit new user-approved subbatches, each independently qualified and enabled:

| Proposed subbatch | Endpoints | New starts | Maximum whole-endpoint result |
|---|---|---:|---:|
| FWT_MAIN61_RESTORATION_PROPOSED | FWT S and F on exact qualified main61 | 2 | 2 × 384 MiB |
| SGEMM_MAIN61_EXPLORATORY_PROPOSED | SGEMM S and F on exact main61 after its own E qualification | 2 | 2 × 384 MiB |

The maximum four starts would bring cumulative actual count from 46 to 50. Old INCOMPLETE/RESOURCE_LIMIT, HOLDs and costs remain; failure consumes a new start and grants no automatic replacement. These conditions are not covered by the completed ten-condition capacity batch. Main61 is not replaced by the capacity binary, and neither new SGEMM qualification nor old FWT qualification may be inherited across binaries.

Applications receive 1,610,612,736 B total (1.5 GiB) for their four whole-endpoint caps. Separately propose at most 134,217,728 B (128 MiB) for any genuinely missing small qualification evidence and 33,554,432 B (32 MiB) for collector/central sidecar metadata outside those endpoint directories. These are conservative additional allowances, never an excuse to enlarge the 384 MiB endpoint caps, duplicate passed tests, or bypass resource/native authorization. Missing qualification scope must be reviewed before any such test, with the original lease. If it cannot fit, stop the affected not-yet-started condition and revise the proposal; do not silently expand this allowance.

The complete proposal envelope is 1,778,384,896 B (1.65625 GiB), leaving 2,059,775,024 B new-generation headroom and 2,782,584,176 B total-generation headroom at this snapshot. It is **not reserved**. High I/O alone is not a refusal reason.

## Parallel pipeline and completion expectations

The unchanged original resource gate was evaluated against deep-copy forecast rows, without a lease or registry write: one, two, three and four concurrent 8 GiB / 1 CPU endpoints all fit this snapshot. Four endpoints exhaust the shared 32 GiB reservation quota; a native qualification cannot overlap all four under that quota. Complete any required bounded native qualification first, or leave the appropriate physical reservation available. Every actual launch must rerun transactional admission, including active other clients and outstanding disk growth. If only one endpoint fits, run it without waiting for its mate. Do not impose a two-route limit, nor promise four-way execution merely because this snapshot fits.

FWT historical priors are approximately S 80–110 min and F 85–120 min per endpoint; these are not acceptance timeouts or guarantees. SGEMM complete-application walltime is UNKNOWN; its prior approximately 837-second trace scan is not simulation runtime. Thus whole-batch finish is UNKNOWN until SGEMM has valid progress data. Four-way eligibility would allow the two pairs to overlap; no absolute finish time is defensible now. No old deadline or 10,800-second timeout is silently restored. Effective central numeric start/deadline/per-end time fields are null, but the old exact approval does not authorize these four new conditions. The proposed future four-condition operational timeout is `timeout_seconds=null`, with all resource guardians, progress evidence, normal exit and independent terminal checks retained; this exact new scope requires user approval before adoption.

Keep each lane busy only where a real dependency exists:

1. D immediately consumes the already-delivered fifth capacity pair, reuses its first-four-pair cache, and publishes incremental figures and the separate five-workload diagnostic conclusion while E2 reviews future inputs. D need not wait for future workloads.
2. E2 consumes the already-delivered A2/C/F packets once, completes exact FWT reuse review and SGEMM independent coverage, and publishes two complete proposed subbatch manifests. It alone owns later central admission and execution. It reports each completed pair immediately to D; no all-workload barrier.
3. A2 and C remain available for exact deficiencies discovered in the existing main61 SGEMM config and empty-fallback binding. Request one consolidated correction per owner, rather than resending already-complete preparation tasks or asking them to rebuild.
4. F can independently investigate the seven precise BFS provenance/input/oracle gaps as a future metadata-preparation lane if separately dispatched; BFS does not block the FWT/SGEMM proposals and gets no application start from them. Hotspot stays reserve; B has no repeated W/V work.
5. Delivery uses the shared immutable queue and existing approval relay; sender delivery is not recipient ACK or scientific acceptance. A lane finishes a task by publishing evidence and its real STATUS, and takes the next dependency-ready assigned item at a safe boundary. An idle conversation still needs a user wake message where the transport cannot wake it; no daemon, background poller or extra controller is proposed.

This read-only review performs zero native tests, builds or complete applications. It changes no scientific cohort or result qualification.
