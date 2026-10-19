# AG6 strict / typed statistics: source handoff

**SOURCE_PREPARED_NOT_EXECUTED.** No import, AST/syntax compilation, self-test,
old/new stdout parsing, resource query, build, canary or simulation was run.
Only immutable source/contract metadata was read. This module has no CLI,
filesystem/process/clock/network access or writes. It imports only Python's
standard csv/hashlib/io/json/re modules; it never imports frozen `common.py`,
the old runner or the old strict CLI.

## Frozen source correspondence

| Input | Commit / path | SHA256 |
| --- | --- | --- |
| Scientific implementation source | `d8d0401dab0a1d9cb949302bcc05148328421cc2`, `docs/dtc_l1/review_packs/DTC_LANE_AG4_AUTHORITY_AE_AD_V1/tools/strict_screen.py`, blob `a94bb199ab3249a57cf7c9c6234e5ef1ad2b4f92` | `9dbbca9c49836619f5ca5ce80d1cd2b9265d3d83d59a5f585510110bcc29aaa6` |
| Actual AG6 four UUID preregistration | `f7246c5d8a2401c23c4b50be051af1585a49cf42`, `docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json`, blob `3037a3b8c9acecea292266c482e52b599ee1ad05` | `844591f608ff99203b22f7f7cb958e1c7633726c3e351da7b7407dd53edee38e` |
| Reviewed scientific manifest | same parent commit, `execution/ag6_final_prep_intake/AG6_FOUR_ARM_SCIENCE_PROPOSAL.json`, blob `f90bbbda96294790161d4d7982353789eb2aac26` | `5e06ba311cb40bfde23153c6760df878a38d4d2e4bbefb2f793b424df203dd15` |
| Existing ordered kernel metadata | AG4 commit above, `docs/dtc_l1/review_packs/DTC_LANE_AG4_AUTHORITY_AE_AD_V1/inputs/T/inputs/KERNEL_BODY_AUDIT.tsv`, blob `c7bbdb55e577006b2313c62674264179066447ff` | `164157917d13768ae0ae4dbdd545b761d0a9bbd5e57c5b5480bb0bac7bed7ef5` |
| Typed dictionary | AG4 commit above, `docs/dtc_l1/review_packs/DTC_LANE_AG4_AUTHORITY_AE_AD_V1/METRIC_DICTIONARY.tsv`; byte-identical parent `execution/ag6_final_prep_intake/FROZEN_METRIC_DICTIONARY.tsv` | `5d24ac7aa85ca30eb9defd51c420876f4a4a4f2475ffe65346e1c355e38f47ec` |

`execution/` paths in the table are relative to the same plan directory. These
four data inputs are caller-provided **exact bytes**, checked against constants
inside the module, not against their own declarations. No audit/body scan or
trace payload hashing is performed. All scientific fields from the reviewed
proposal are joined to the actual preregistration; its placeholder
`new_attempt_uuid` is replaced by the fixed actual UUID, and its proposal
cohort label is explicitly joined to the fixed actual cohort label (see the
source-only schema correction below). The parser accepts
only AE_GEMM / AE_Gaussian / AD_GEMM / AD_Gaussian, not BASE, AC, AF or a fifth.

`echo`, `numeric`, `traffic`, `parse_full` and `pipeline_contract` preserve the
AG4 scientific conditions, rewritten as pure functions. The former implicit
PACK files become the exact-hash injected preregistration/audit. Full parsing
retains command and memcpy order, exact member paths and kernel names/UIDs,
one natural/thread exit, real initialization and forbidden-signature checks;
each kernel checks its full active instructions and cumulative CTA/insns,
terminal Ref/ownership/credit drain, lower create/inject/response conservation,
source sidecars, physical640x64 capacity/allocation and finite-service scope.
All finite cumulative fields remain monotonic; samples equal64*totalcycles.
Final CTA and instruction totals must also match the point registration.

The full270 echo must equal the frozen point's exact option dictionary. Fixed
K0/OO128/Tag64x8/physical640/allocation4/finite1 is explicit. AE requires
tag_hash1/wakeup0; AD requires tag_hash0/wakeup1. No AC export is accepted.
AD OFF's ON-only frame is unavailable rather than zero. AD ON uses the last
complete64SM frame, exact33-bin fanout population, span and retired joins.
Additional conservative checks reject duplicate DRAM fields, malformed extra
AD frames, nonpositive total cycles and duplicate JSON keys. The source has
not been executed to establish equivalence or qualify these additions.

## Parent call and exact receipt schema

Parent may bind/import this source only after its own source registration and
admission. `parse_attempt(point, **inputs)` accepts the following bytes, with
the names shown in its signature:

- `stdout`, `stderr`: complete new actual simulator streams, not a prefix or
  a previous point. Their SHA256 appears in the output.
- `run_start`: actual exclusive RUN_START.json, with point, attempt_uuid,
  order, source_core, timeout_seconds7200, retries0, argv and ordered
  config_copies[{path,sha256}]. Its argv must be the registered runtime,
  original trace list and these exact copied config paths. This is a proposed
  source-bound AG6 wrapper schema, matching frozen AG4 wrapper fields; no such
  new wrapper receipt is fabricated or claimed to exist here.
- `run_terminal`: actual RUN_TERMINAL.json with returncode0, forced_reason
  null, identity_pass true and `engine` equal to the independently supplied
  `engine_terminal` JSON object.
- `engine_terminal`: original canonical AG5 guard ENGINE/TERMINAL.json fields,
  not a normalized status invented by the parser. Required successful fields
  are status PASS_GUARDED_NATURAL_EXIT0, purpose SIMULATION, root_pid>0,
  returncode0, forced_reason/exception null, identity_pass true,
  simulator_starts1, snapshots>0, owned_children_live0,
  unconfirmed_wait_pids[], ownership.confirmed[], ownership.pending[],
  ownership.retired and owned_process_exit_instances. Unique PID/start_ticks
  exit instances must join the retired instances and contain the natural root
  exit; all exit codes are0. The old PID-only owned_process_exits dictionary
  cannot replace the generation-specific list.
- `preregistration`, `science_manifest`, `kernel_audit`, `metric_dictionary`:
  exact immutable bytes from the table, not reconstructed JSON/TSV.

Every valid own RUN_START consumes one observed reserved slot **before** later
terminal/strict checks. A malformed/STOP guard does not refund it. A positive
guard root_pid proves one actual direct fork; only a null-root canonical fork
failure's explicit actual_fork_children0 proves zero. Successful canonical
guard terminals do not currently emit actual_fork_children: the parser does
not require that absent field or call a reserved slot an actual child. Missing
fork evidence remains UNAVAILABLE. This report is a per-attempt observation,
not an authoritative global ledger; parent enforces unique UUID/start order,
at most4 starts and no retry/replacement/canary independently.

## Statistics and acceptance limits

`typed_statistics` always reads **only final_metrics**, final traffic or the
last AD frame. Gaussian510 kernel cumulative snapshots are never summed.
Unit, source, denominator, population, comparability and missing policy are
preserved verbatim from the fixed dictionary. Means use exact numerator and
denominator integers; zero denominators remain undefined. Missing/OFF values
stay null with UNAVAILABLE, including overlap, conflict distributions and K1
data. The AD-only fanout/span/own-dep0/return-retire diagnostics retain their
ON-only population and cannot be subtracted from a BASE missing field.
Summing64 SM rows **within one last cumulative AD frame** is the specified
population aggregation; summing kernel snapshots is forbidden.

L2 accepted GLOBAL_ACC_R sectors are HIT+HIT_RESERVED+MISS+SECTOR_MISS and must
equal TOTAL_ACCESS. DRAM issued read/write atoms are kept separate across20
controllers, multiplied by32B; uninitialized n_ref is explicitly unavailable.
Collection/WB interval sums do not establish actual overlap. No numeric native
load values, ISA/coherence, RTL, frequency or per-bank histogram is inferred.

The result's `scientific_strict_pass` can become true for supplied bytes;
`performance_accepted` deliberately remains **false**. Parent must separately
join the immutable capability/source/runtime/.so/input/config/map-event,
resource/authority and terminal receipts to prove those bytes belong to this
actual registered attempt. Embedded version strings, claimed config SHA and
guard identity_pass are necessary fields, not independent proof of identity.
Only the parent's completed actual evidence closure can admit the integer
cycles or calculate BASE/ON ratios. The parser does not select F, change O,
release a role or dispatch anything.

Remaining: parent static review/freeze, explicitly admitted import/parser
qualification and actual four-point integration are unexecuted. There is no
new self-test source or execution proposal in this delivery. Parent may retain
all failure reports and existing selection/budget without a new run.

## Source-only schema correction after first actual adapter call

Parent `2a88ddd600848a794b8bb5322b01f042eaeb5c0b` reported that actual admission
passed but the first frozen-contract case rejected with
PREREG_SCIENCE_FIELD_MISMATCH; identity/map calls and simulations remained0.
Static comparison of all four actual preregistration/science JSON rows found
only two differing proposal fields: new_attempt_uuid's expected assignment and
the cohort label. The original parser handled only the former; treating the
valid label transition as scientific equality was an implementation error.

The corrected source explicitly requires proposal cohort
AG6_V2_FOUR_ARM_DISCOVERY_WITH_TWO_QUALIFIED_IMPORTED_BASES and actual cohort
AG6_DISCOVERY_V2_ORIGINAL174_FOUR_START_ONLY, plus the original UNASSIGNED_BA_ONLY
proposal UUID. Only those two known fields leave the generic equality loop;
every other proposal field still compares exactly. The four immutable metadata
hashes, actual UUIDs and all scientific checks are unchanged. The existing
first targeted case now asserts the fixed label pair, with no extra case.
Current parser SHA256 is
`9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4`.
This worker did not import, run or qualify the correction. The failed actual
attempt remains preserved; a new exact outer path/source release/admission is
owned by parent, with no UUID, data or science change.
