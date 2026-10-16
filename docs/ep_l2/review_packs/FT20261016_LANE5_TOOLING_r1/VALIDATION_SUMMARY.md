# Validation and limits

Tooling producing commit is recorded in SOURCE_MANIFEST, separately from this
evidence publication's future SHA. Tests are rerun after freezing source.

- Python: 39/39 unittest methods PASS; the final raw output is retained.
  Includes 8 competing processes with exactly one fresh run-key claim and one
  shared lease token, cross-lane reuse, scan exclusion, resource floors,
  duplicate/failed-key preservation, full config/trace identity, qualification
  rejection, wrong data/version, stale tag fill and premature lifecycle frees.
- Historical Core: frozen 1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e, clean
  tracked tree before compilation. `run_payload_store.sh` (includes sector
  lifetime), `run_payload_banked.sh`, and `run_descriptor_mshr.sh` PASS.
  Output binaries and logs go to private TMPDIR under validation_r1; no existing
  simulator executable was rebuilt. The shared 1-CPU / 4-GiB build lease was
  released after completion. Heterogeneous stages are not counted as B16 runs.
- Roster: 13/13 historical list hashes match; every referenced kernel file
  exists. Full trace-body hash is deliberately deferred to actual qualified
  runtime admission, not substituted with the list hash.
- Formal new finite-WBUF performance runs: 0. Lane 1 consumed release remains
  PARENT_IDENTIFIED_RUNTIME_VALIDATION_PENDING, runtime_ready=false,
  binary_sha256/config_sha256=null. No production qualification envelope exists.

Remaining production adapter gates include atomic ordering, preview/reserve/
rollback, real finite-WBUF pressure, same-bank progress, partial sectors and
response backpressure. TVD/RO need their additional source-version checks.
The current reference oracle supports explicit initialized sector read/write
sequences; unsupported atomic/concurrent semantics fail closed rather than
being silently accepted. A test-only synthetic envelope is used solely by
runner input self-tests; it is never written as a production release artifact.

Historical WB semantics were read from frozen Motivation plan and Streaming
Core ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919 L2interface::push:
the real L2-to-DRAM FIFO push precedes the lower-accept observation. Payload
staging ends at accounted lower data handoff; WAD persists to actual set_done.
Historical shadow capacities do not establish a finite physical buffer result.
