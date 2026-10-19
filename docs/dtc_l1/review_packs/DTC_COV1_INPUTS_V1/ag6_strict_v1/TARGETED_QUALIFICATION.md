# Four targeted parser interface cases

Status: **SOURCE_PREPARED_NOT_EXECUTED**. This delivery contains source and
expected assertions only. No import, AST/syntax check, parser/test call, raw
read, subprocess, build, resource sample or simulation was performed. The
parser now includes the source-only exact cohort-label schema correction at
SHA256 `9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4`;
its prior8816 version from COV `6916beef86b495461bf4da64ae9d6dcbb554eb5f`
failed the parent's first actual case before identity/mapping work. The four
cases remain fixed; the first now also asserts the exact label transition.
Current parent context is `0ec58e0733ef27e858438a92f5a04d7f91b041ab` /
`ffc8015bd8e2ff4cd526d115100ebd44d98a0c1e`.

`targeted_qualification.py` has one parent-callable entry:

```python
report = qualify_targeted(
    source_bound_parser_module,
    parser_source=exact_frozen_parser_bytes,
    preregistration=exact_preregistration_bytes,
    science_manifest=exact_science_manifest_bytes,
    kernel_audit=exact_existing_audit_tsv_bytes,
    metric_dictionary=exact_dictionary_tsv_bytes,
)
```

The source does not import a parser by path/name or load any files. Parent
must bind the injected module object to the actual frozen source/import
closure; matching a supplied byte string alone cannot prove an arbitrary
module object's origin. The four metadata inputs remain the exact immutable
Git bytes listed in the adjacent README, enforced by the existing parser's
fixed hashes. This is metadata reuse, with no new trace audit or raw stdout
read. There is no CLI, writable output path, process, timer, retry, discovery,
resource check or runtime permission in this callable.

| Fixed case | Assertions / expected outcome after an actual admitted call |
| --- | --- |
| `case_frozen_contract` | Exact four point/UUID pairs, frozen GEMM metadata and fixed proposal-to-actual cohort labels accepted. Replacing one UUID byte string rejects with `FROZEN_INPUT_BYTES_CHANGED`; BASE_GEMM rejects with `FOREIGN_OR_BASE_POINT`. The test does not repin hashes to make edited metadata admissible. |
| `case_guard_reserved_boundary` | A declared canonical guard with nonempty pending rejects with `GUARD_CURRENT_OWNERSHIP_NOT_DRAINED` while reserved_start_slots remains1; positive declared root records fork1. A canonical fork-failure declaration retains reserved1 and records fork0 only with explicit actual_fork_children0. Removing that field leaves fork count UNAVAILABLE, never guessed0/1 and never refunded. |
| `case_final_cumulative_and_off` | Two declared kernel cumulative cycles7 then13, PIB integrals35 then91, produce final cycles13, PIB91 and samples832. Exact mean is91/832, not126/1280. AD-OFF span and unexported collection/WB overlap remain null/UNAVAILABLE, not numeric0. |
| `case_exact_options_and_single_arm` | Two complete minimal declared GEMM fixtures reach scientific byte-check PASS under exact270 AE and AD dictionaries; AD includes one complete declared64SM/33-bin frame. Removing an echoed option or enabling AD while AE remains on rejects at `all_270_effective_options_exact_population_and_values`. Every report retains performance_accepted=false. |

These are four fixed cases with finite grouped assertions, not a new general
test framework or a rerun of prior AG4/AG5 negative suites. The source creates
its small strings/dictionaries **only when called**. Every generated simulator
stream/guard/start object is explicitly **DECLARED_SYNTHETIC**. No actual
simulator, guard, launch identity, mapping, real trace access population or
scientific result is qualified by those fixtures. Fixed real GEMM names,
counts, version strings and options are necessary to reach the exact interface
branches; their presence in a fixture is not execution evidence. The parser
and test both preserve performance_accepted=false for such declarations.

The cumulative selection test calls `parse_full` with two expressly declared
rows, then passes its actual `final_metrics` into `typed_statistics`; it does
not merely hand a final scalar to a duplicate implementation. The option and
guard cases call the actual `parse_attempt`, so their checks cover its ordered
early budget boundary and exact-option failure path. The four-UUID mutation
is rejected at the original immutable hash gate, with no parser patching or
monkeypatch to bypass provenance. No real calibration stdout is needed or
proposed for these four cases.

Before actual execution parent must publish exact qualification/parser/source
and four metadata hashes, a source-bound CPU entry, output/total bounds and
fresh full-R2 admission. Suggested narrow outer bounds are60s total and1MiB
output, one foreground invocation, with no child creation by this callable.
These are proposed limits, not a measured runtime or release. A failed
registration/admission must retain0 executed cases; do not import/call this
entry before the admitted outer start receipt.

On actual invocation the function returns four PASS case rows only if all
assertions ran successfully. It stops on the first case failure and returns
FAIL with the actual number reached; pre-case source-hash binding failure
raises and must be preserved by the parent's outer terminal receipt. Parent
must keep actual release/admission/START/terminal/output receipts alongside
the returned report. This source publication itself is **0 cases executed**.
No helper's in-memory status or fixture PID constitutes a real launch receipt,
and no simulation budget, selection, BASE qualification or AG4 contract changes.
