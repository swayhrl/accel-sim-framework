# CPU raw evidence index

Node109 root: `/data/c16/dtc_sm89_admission_feasibility_109_v1/`. RAW_LOG_INDEX.json SHA-lists every archived file.

- `raw/PREFLIGHT.txt`: fetched source/worktree/task/lock/host snapshot; read-only lock inspection.
- `raw/LOCAL_DISTINCT_DECODERS.json`, `raw/SOURCE_INVENTORY.log`, `assets/*trace_driven*`, `assets/*ampere_opcode*`, `assets/*trace_parser*`: bounded source artifact inventory and immutable source snapshots.
- `raw/PARSER_BUILD.log`, `raw/PARSER_LINKED_LIBRARIES.txt`, `build/parser_probe`, generated dispatcher fragments/binaries: host-only build/probe evidence.
- `raw/PARSER_KERNEL_0.tsv` through `_3.tsv`, `raw/CPU_AUDIT.log`, `raw/TYPED_DEPENDENCY_FIXTURES.tsv`: exact parser outputs and audit results. Git compact receipts/coverage contain the conclusions.
- `assets/cubin/*.cubin` and `*.liveness.txt`, `raw/CUBIN_EXTRACTION.log`: offline original-executable inspection. No native launch.
- `raw/OPTIONAL_REFERENCE_DOWNLOAD_STOP.json`: only this task's slow optional HTTP metadata fetch was stopped after source inventory finished; official archival pages were independently read using web. No project/payload/toolchain change. CPU reproduction has no HTML download dependency.
- `raw/CLOSEOUT_CPU_STATE.txt`, `raw/VALIDATION.log`: final host/check state.

Original native files remain at their existing paths and are not copied into Git or edited. Producer/consumer byte hashes and source snapshots are sufficient to bind this independent audit. The local CPU archive and its SHA are recorded in CPU_ARCHIVE_RECEIPT.json. It is a new file, not a replacement of the previous native archive.
