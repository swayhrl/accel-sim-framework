# C14 dual-path exploration — final report

Status: `C14_DUAL_PATH_EXPLORATION_COMPLETE_READY_FOR_REVIEW`

All C14 microdiagnostics are terminal `PASS` except the explicitly retained
`CONFIG_REJECTED_SUPERSEDED` initial N configuration attempts.  Every
scientific row is labelled `EXPLORATORY_MICRODIAGNOSTIC` and
`STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT`; C14 launched no full-ROI matrix.

## Decisions

| Question | C14 answer | Evidence boundary |
|---|---|---|
| Is Segment-path redundant exact translation work worth eliminating? | **No — P `NO_GO_WITH_EVIDENCE`.** | C12 already delays L2 until joint L1/Segment miss.  Every observed Segment winner had no L2 issue, MSHR allocation, PTW start, or PTE issue. |
| Is requester latency decoupled from exposed GPU stall? | **Yes as a non-equivalence; not as a global-stall measurement.** | Requester/head aggregate cycles can overlap heavily.  N E/O has `288031809` accumulated requester/local-head cycles but `17581197` GPU cycles.  The Decode high pair removes `24245368` aggregate cycles for only `28797` GPU cycles. |
| Path P GO? | **NO_GO_WITH_EVIDENCE.** | Only the admission-time L1 port races Segment; it is spent before result and lacks a safe reversible handle. |
| Path N GO? | **GO_OBSERVATIONAL_ONLY.** | Default-off local `LOCAL_LDST_HEAD_PROXY`, ready-to-data-admission gap, occupancy, and object/outcome reporting are validated.  No policy mechanism or global critical-path claim is authorized. |

The first P evidence cell intentionally does not aggregate different traces:
the strongest hot E/O receipt alone has `16420796` Segment winners, each with
all four downstream-not-started counters equal to `16420796`.  Full rows are
in `MICRODIAGNOSTIC_RESULTS.tsv`.

## P conclusion

Source audit establishes the real order: requester admission consumes L1
lookup capacity, then L1 and Segment service in parallel; a Segment hit
finishes the requester.  L2 probe, translation MSHR, PWQ/walk/PTE work begin
only after both upstream lookups miss.  Thus the proposed
Segment-before-L2 gate is already present.  The other candidate,
opportunistic cancel-before-admission, has no safe local cancellation
boundary: L1-port consumption is irreversible and downstream work may be
shared by MSHR waiters.  C14 did not implement an unsafe duplicate/cancel
mechanism.

The default-off P telemetry did not perturb timing.  Its direct unit receipt
and the `P-AP-L7` telemetry off/on trace receipt retain identical simulated
cycles (`138163`) and conventional translation counters.

## N conclusion

C14 N intentionally distinguishes terms rather than claiming a global
critical path.  `vm_translation_requester_latency_cycles_total` is a
translation lifecycle aggregate.  `HEAD_BLOCKED_CYCLES` is a bounded local
LDST-head proxy, currently equal in total on the sampled accesses because it
increments for the same pending head; it is nevertheless attributable by
object/outcome and paired with ready-to-data-admission observations.  Data
admission is explicitly weaker than memory/DRAM issue.

The high Decode cold pair demonstrates why aggregate translation suppression
must not be reported as a performance ratio: F0 to F7-L5 decreases requester
and local-head aggregate from `58685284` to `34439916` while simulated cycles
decrease only from `3758863` to `3730066`.  The low selector reverses the
accepted full-ROI near-zero ranking in cold replay (`-682` cycles), which is
direct evidence that the micro context is not ROI-equivalent.

## C13 dependency and priority

The final read-only C13 fetch is
`9ab1e0708af66a533d9327f35f1a3e63a34c4285`:
`C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`.  EQ1/EQ2 promote
the repaired L2-mode-0 evidence; the old nine mode-1 rows remain
`SUPERSEDED_WRONG_L2_MODE_SUBENTRY16`.  C13 still does not establish queue,
DRAM, or global-critical-path causality.  Therefore it raises **N** from a
conditional diagnostic to the preferred next measurement on one repaired,
pre-registered full-ROI pair.  It does not change **P**, which is closed by
independent source and runtime evidence.

## Next formal work (at most three)

1. Decode1 F0 vs F7-L5 pair with N telemetry: 2 serial runs, about 18–24
   simulator-hours total, 1–2 GiB RSS per simulator.
2. C13-repaired Prefill F0 vs L9 exact-mode pair with N telemetry: 2 serial
   runs, about 28 simulator-hours total, 1–2 GiB RSS per simulator.
3. One C13 adjacent-bracket Prefill confirmation with N telemetry: 1 serial
   run, about 14 hours, 1–2 GiB RSS.

These are proposals, not work started by C14.  See
`NEXT_FULL_ROI_EXPERIMENTS.md` for constraints and acceptance conditions.

## Review entry points

- Translation map and race order: `COMMON_TRANSLATION_PATH_MAP.md`,
  `CURRENT_SEGMENT_RACE_TIMELINE.md`.
- P and N mechanisms: `PATH_P_REPORT.md`, `PATH_P_PROTOTYPE_AUDIT.md`,
  `PATH_N_REPORT.md`, `PATH_N_INSTRUMENTATION_AUDIT.md`.
- Reproducible terminal rows: `MICRODIAGNOSTIC_STATUS.tsv` and
  `MICRODIAGNOSTIC_RESULTS.tsv`.
- Decisions and C13 dependency: `GO_NO_GO_MATRIX.tsv` and
  `C13_DEPENDENCY_SNAPSHOT.md`.
