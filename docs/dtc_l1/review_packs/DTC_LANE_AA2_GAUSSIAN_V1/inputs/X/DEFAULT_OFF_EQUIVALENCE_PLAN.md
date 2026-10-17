# Default-OFF equivalence: implemented controls and remaining gate

Status: `LOCAL_CPU_AND_STATIC_EVIDENCE_ONLY_FULL_SIMULATION_EQUIVALENCE_UNPROVEN`.

The new production option is `-gpgpu_dtc_l1_invalidate_on_source_event`,
registered as `OPT_BOOL` with default `0`. The production shader configuration
registration and parser are exercised with the option omitted, explicit `0`,
and explicit `1`; omission/0 is false. K1 requires PAPER_OO. IO and modern/Base
K1 are explicit unsupported failures; K0 retains all old mode support.

## Evidence delivered now

- Four existing directed regression targets passed on the new source.
- New K1 tests pass locally and do not relabel the historical four tests as K1.
- The same deterministic K0 trace source was compiled against the frozen header
  and the new header with matching compiler/optimization/assertion settings;
  IO/OO with finite service off/on, Base and modern traces match byte for byte.
  This covers those CPU mechanism sequences, not arbitrary full LD/ST execution.
- Frozen ordinary cache files, IO/modern frontends, response routing, admission,
  lower-request creation, writeback and core source-event predicates are checked
  against the new source. The event callers differ only in diagnostic labels.
- Source SHA/content identities are recorded before and after the fresh build and
  tests. The released libcudart embedded SHA and the test library resolution
  identify the new clean Core build. Earlier dirty/incremental build candidates
  are excluded, not relabeled as the clean release.

## Remaining formal verification protocol (Lane Y gate)

1. Review the published Core/Framework identities, Lane V immutable contract and
   all source changes. Check omitted/0 in actual LD/ST source events as well as
   parser/default behavior; no source request may touch DTC visibility for K0.
2. Use separately built binaries and identical complete configuration, inputs,
   traces and compiler/assertion settings. Freeze binary/config/parser identity
   before execution and recheck own source identity afterwards. Never overwrite
   prior frozen products or enter another Lane's changing result directories.
3. Compare architectural completion, simulated cycles, every existing mechanism
   counter, lower traffic, credit/dependency/Ref balance and drain. Normalize
   only documented build strings, wall time and host throughput; unexplained
   legacy-counter differences fail equivalence.
4. Exercise all existing K0 modes, including IO, modern and Base/LEGACY. For K1
   check only OO. Verify real source-selected SM sets and invocation order for
   repeated idle events, MEMBAR and config change with ordinary pending/drain.
5. Extend CPU coverage to actual LD/ST sector returns and operand-collector WB
   refusal. The current predicate/helper tests do not establish full runtime
   integration or architectural values. Keep value and all-ISA claims unproven.
6. Only after Lane Y qualifies the implementation may a separate authorized run
   window start full OO-only performance matrices. This window starts none.

Controls differ only in the new option. Preserve original flush settings,
finite-service settings/quotas, PIB, capacities, clock, lower cap, kernel work
and input/trace. No posterior performance threshold participates in semantics.
