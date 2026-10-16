# DTC ISCAS2027 experiments: living register V1

Created 2026-10-16. **This is a planning and evidence-index branch, not an execution branch or a new start command.** Existing 174 Goal continues unmodified; 109 producer finished.

- [MASTER_MATRIX_V1.tsv](MASTER_MATRIX_V1.tsv): master scientific questions, priority, exact authorized scope, state at referenced remote snapshot and stopping rule.
- [MASTER_MATRIX_V1.md](MASTER_MATRIX_V1.md): readable table including all closed/conditional experiments.
- [EXECUTION_PIPELINE.md](EXECUTION_PIPELINE.md): rolling schedule, dependency gates and resource safety.
- [PAPER_SETUP_REQUIREMENTS.md](PAPER_SETUP_REQUIREMENTS.md): data-backed config summary, what must appear in IEEE manuscript, 3 ISCAS original-paper examples.
- [UPDATE_PROTOCOL.md](UPDATE_PROTOCOL.md): how experiment jobs and this overview get updated after strict receipts.

**R1 V2 accepted:** e1c474f, Core6fba013; prior R1 V1 pipeline test/attempts superseded; 174 R2 registry 44 rows preregistered in original execution branch. **109 native completed:** 890fb0be; LayerNorm trace not admitted, SpMV pending 174 consumer. **Modern DTC fixed budget:** e13266 decision128KiB, 174 capacity audit HOLD; 208KiB hypothesis cannot be equal-budget comparison.

Neither the registry nor experimental paper-method corrections reassign ownership, change accepted data, trigger simulators, overwrite the latest Goal, or authorize new protocol changes. Later snapshots must identify new commits and evidence; this first one contains NO new simulated result.

## 2026-10-16 latest synchronized checkpoint

**[Master status V2](MASTER_MATRIX_V2.md)** / [TSV](MASTER_MATRIX_V2.tsv) / [Source checkpoint analysis](CHECKPOINT_20261016T0918Z.md). Updated after independently fetching174 commit `59e1fd9b`: 44 registered = 3 strict PASS, 6 running, 35 not launched at UTC09:17 snapshot. Three PASS are Btree IO/OO/TRAD96. Same-arm cohort gate is now eligible without waiting for all pilots. 4080 baseline-only four passed, modern DTC still held. SpMV canary NOT_ADMITTED on SM89 dispatcher; LayerNorm trace NOT_ADMITTED. V1 is historical and preserved.
