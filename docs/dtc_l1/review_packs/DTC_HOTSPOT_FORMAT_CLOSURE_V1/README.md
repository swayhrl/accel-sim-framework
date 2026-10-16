# Hotspot historical format provenance — original174, V1

Status: **INDEPENDENT_DERIVED_CANDIDATE_REVIEW_PREPARED; HOLD_UNCHANGED**.

**Current continuation:** the user selected continued V2 research as an explicitly independent new derived-input candidate, without confirming historical ELF equivalence. See [DERIVED_INPUT_QUALIFICATION_CANDIDATE](../DERIVED_INPUT_QUALIFICATION_CANDIDATE/README.md) for the fresh185-PC/raw-address/differential checks, exhaustive actual-change index and limited eleven-input review. That review found separate Btree/LUD/2DConvolution risks separately assigned bounded CPU-only review by the user; those reviews do not block Hotspot delivery. Original ELF recovery is no longer a prerequisite for this candidate research; no admission, HOLD release or simulation was authorized. The V1/V2 narrative below is retained as evidence history, not a new request to choose the old alternatives.

**V2 continuation:** a CUDA9.1 frontend/CUDA10.1 assembler reconstruction now matches the entire fixed member's185 observed PC/opcode-root/GPR signatures and over20 million explicit raw lane addresses. A concrete isolated normalizer candidate narrows the changes to122760 records at six PCs. See [the V2 evidence and candidate](source_profile_v2/README.md). This is a source-model qualification, not a receipt proving the original capture binary's identity; admission still requires the semantic/input review described in NEXT_DECISION. The original V1 conservative inventory below remains preserved.

The historical implementation explains the sparse-mask records, but does not authorize a unique repair of this fixed input. No address repair was selected. Main parser, trace, Core, runtime binaries, admission holds and launch authority were left intact. This helper used one CPU scanner/check process, an isolated small C++ oracle build, and no GPU or simulator.

The dedicated branch is `hrl/iscas2027-dtc-hotspot-format-174-v1`; worktree `/workspace/worktrees/accel-sim-iscas2027-dtc-hotspot-format-174-v1`; outputs `/workspace/dtc-hotspot-format-174-v1`, including its own `build/`. The branch contains required documentation commit `7112a2242c81bc6aed82a1077b3e68abd6771ea3` and main execution snapshot `07503e6dc5a39a650a34986ddff3b458faea9f59` through an independent merge. Running build Framework remains `18a68dcccd795f1b6cda75504e9450d00c9cee02`, finite Core `6fba0136f8465b59fe5858a950fa39efb265f654`, runtime SHA `fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b`. Helper source identity is not substituted for any runtime identity.

## Source closure achieved

1. The original staged member is byte-identical to the Hotspot member inside the retained `rodina-3.1.tgz`: 1041309456 bytes, SHA `ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8`, tar header offset `6632942080`. This is payload identity, without claiming a hash for the whole archive. The bounded archive pass stopped after the contiguous Hotspot subtree. It recorded 20 entries, including both 512 and 1024 recipes; only the fixed 1024 member was body-audited.
2. The archived launcher names CUDA9.1, historical `traceall.so`, the `1024 2 2` command, postprocessing, and deletion of `*.trace`. No ungrouped trace, tracer library, ELF or cubin occurs in that subtree. The data directory is an external symlink. `stats.csv` contains only its header. The command is now source-backed; original temp/power bytes and executable/library hashes remain missing. No packaging loss was mistaken for scientific payload loss.
3. Historical March2020 tracer source prints `P = active_mask & predicate_mask` while compressing/listing addresses with `E = active_mask`. Its instrumentation collects addresses for execution lanes even when their predicate is false. The August2020 encoder still requires contiguous **E**, so sparse printed **P** is possible. The postprocessor groups unchanged instruction strings; it does not repair operands.
4. Upstream commit [756ed33d, 2020-11-06](https://github.com/accel-sim/accel-sim-framework/commit/756ed33d503704b4faf97bb3a051792f0450d14c) corrects the address mask to `active_mask & predicate_mask`. This confirms a historical producer defect; it is not a historical consumer format definition. Header, launcher, timestamps and body fingerprints strongly match that family, but do not bind an exact producer binary to the capture. The old inventory label `NVBit-v1.4-text-traceg` must not be used as proof of an actual NVBit1.4 capture: the header has no such field.

See [SOURCE_REGISTER.tsv](SOURCE_REGISTER.tsv), [source hashes](GIT_SOURCE_HASHES.tsv), [archive receipt](ARCHIVE_RECEIPT.json) and [capture metadata](CAPTURE_METADATA.json). Facts, inferences and missing bindings are separate register entries.

## CPU results and new scope finding

[26 tests](CPU_TEST_RESULTS.json) execute the extracted March inline encoder, August encoder, frozen mode1 decoder and frozen mode0 loop. They cover nonzero first lanes, holes, multiple runs, positive/negative/zero stride, zero/nonzero base and actual `LDS.U`/`STS` width4. Explicit raw address vectors are independent references. The original oracle function SHA `564f5333...` and complete parser SHA `f63db893...` match the prior receipt; active lanes2/15/18/31 reproduce `128/180/0/0`.

Two different raw fixtures accepted by the same historical encoder produce the identical serialized `(P=fffcfffc, base=128, stride=4)`: `E=ffffffff` gives active lane2 address136, while `E=fffffffc` gives128. Both have a valid contiguous execution interval. This is a per-record information-loss counterexample, not a claim that both execution histories match the entire Hotspot binary. Binary/control-flow evidence might eliminate one for a given PC; this task did not establish that for every affected dynamic instance.

One pass over the **single fixed Hotspot member** verified its SHA and the existing counts: 13169524 warp records, 377291004 active-thread instructions. The full629 audit was reused, not rerun.

| Inventory | Records | Meaning |
|---|---:|---|
| Sparse printed-mask shared mode1 | 90792 | Reproduces the original issue |
| Nonzero first printed lane, shared mode1 | 220668 | Hidden execution-base anchor may also affect contiguous printed masks |
| Union of those mode1 classes | 222032 | Includes1364 sparse records starting at printed lane0 |
| Mode0 LDGs with excess address tokens | 3330 | Each carries32 address words despite fewer printed lanes |
| Those LDGs with changed active addresses under full-vector indexing | 2728 | Conditional producer-family interpretation; other602 have no active lanes |

The3330 LDGs occur at PC0180/0190. A source-backed **serialized uncompressed vector** from the fixed member is included in the CPU tests: the frozen parser assigns the first `popcount(P)` entries to printed lanes; historical full-E serialization instead associates all32 entries with lane indices. This can move garbage predicate-off entries onto active global loads. Thus a shared-only decoder change would leave an independently observed global-address concern. Serialized address words are not claimed to be native-correct values.

[DECODER_DELTA.tsv](DECODER_DELTA.tsv) contains124 groups, counts and exact first-occurrence line/CTA/warp/hash, with frozen and explicitly hypothetical address vectors. The complete225362-record risk index is local at `/workspace/dtc-hotspot-format-174-v1/AFFECTED_RECORD_INDEX.tsv.gz`; its hash is in [SCAN_RECEIPT.json](SCAN_RECEIPT.json). The index contains line identities, not an edited trace. [PC counts](AFFECTED_PC_COUNTS.tsv) summarize the dynamic scope.

For the frozen32-bank/4-byte-word/one-part/unlimited-broadcast geometry, the maximum distinct-word count per bank changes from2 to1 on90622 mode1 records under each of the three illustrative hypotheses. See [BANK_SERVICE_HYPOTHESES.tsv](BANK_SERVICE_HYPOTHESES.tsv). Equal bank counts among hypotheses do not establish address equivalence. This is a CPU geometry calculation, not an executed timing result or speedup prediction.

## Impact and handoff

[AFFECTED_ROWS.tsv](AFFECTED_ROWS.tsv) enumerates12 selected historical, reused, registered and modern-baseline Hotspot rows from frozen authoritative ledgers. Terminal validation and scientific promotion are separate fields. Historical receipts are preserved; three unlaunched controls remain held. [HISTORICAL_RECEIPT_DISCOVERY.tsv](HISTORICAL_RECEIPT_DISCOVERY.tsv) inventories11 additional tracked JSON files for reviewer discovery, without claiming an exhaustive census of all old diagnostics or promoting them to primary results. Any other row using this exact member inherits the same interpretation review requirement.

The eleven other fixed workloads have zero sparse mode1 records in the existing audit. That fact does **not** prove they are immune to the newly identified mode0/hidden-anchor mechanism. This helper neither changes their acceptance nor starts a broader scan. Because no runtime or input is changed, their present executions remain byte-for-byte on their original paths. A future global legacy-format repair needs a separately scoped token/mask applicability audit, rather than an unsupported equivalence claim or blanket rerun.

[CANDIDATE_REPAIR.md](CANDIDATE_REPAIR.md) records the initial gated transformation contract; [V2](source_profile_v2/README.md) implements a default-report-only offline prototype against a validated reconstructed source profile. No main-parser patch was installed or interpretation admitted. [NEXT_DECISION.md](NEXT_DECISION.md) provides the source-recovery, reviewed reconstruction/new-input and scope-change choices. A must review source and contract changes, then register new immutable future attempts if authorized. No corrected Hotspot number may be divided by an old-parser baseline, and no Hotspot-omitting aggregate may retain the GM12 label.

## Reproduction

Run from this dedicated worktree, serially, with a fresh separate output directory. No simulator build is needed.

```bash
python3 util/dtc_l1/hotspot_format_archive_v1.py --archive /workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodina-3.1.tgz --output-dir /workspace/dtc-hotspot-format-174-v1/reproduce-archive
python3 util/dtc_l1/hotspot_format_provenance_v1.py scan --member /workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/hotspot-rodinia-3.1/1024_2_2___data_temp_1024___data_power_1024_output_out/traces/kernel-1.traceg --output-dir /workspace/dtc-hotspot-format-174-v1/reproduce
python3 util/dtc_l1/hotspot_format_provenance_v1.py cpu-test --output-dir /workspace/dtc-hotspot-format-174-v1/reproduce
python3 util/dtc_l1/hotspot_format_review_tables_v1.py --diagnostics /workspace/dtc-hotspot-format-174-v1/reproduce --output-dir /workspace/dtc-hotspot-format-174-v1/reproduce-tables
```

Run `scan` before `cpu-test` to include the independent fixed-member mode0 fixture (26 cases; standalone synthetic-only mode is25). Gzip container timestamps can differ across reproductions; decoded index rows and fixed-member identities are the comparison contract. Oracle source warnings about integer signedness originate in unchanged historical code. See [VALIDATION.json](VALIDATION.json), [protected hashes](PROTECTED_BEFORE.json) and [file hashes](FILES_SHA256.tsv).
