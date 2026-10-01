# Deterministic validation

Run `python3 validate_pack.py` from this directory. It checks all required outputs are nonempty, TSV schema and row cardinality, exact experiment-group join to `LITERATURE_EXPERIMENT_CONTEXT.tsv`, source identifiers, evidence levels, NOT_RUN artifact boundary, and final decision invariants. `sha256sum -c SHA256SUMS` independently checks bytes. No paper code or C16 experiment is run by either check.

Research validation is source-level, not performance reproduction. Primary URLs and sections are in `SOURCE_READING_LEVEL.tsv`; author experimental disclosures and absent fields are in `LITERATURE_EXPERIMENT_AUDIT.tsv`, joined on `(source_id, group_id)` to `LITERATURE_EXPERIMENT_CONTEXT.tsv` for research question, phenomenon, author rationale, input generation, evidence type, claim and inference. Every claim of C16 closure is tied to the terminal synthesis authority, not recalculated from raw experimental data in this CPU-only literature stage.
