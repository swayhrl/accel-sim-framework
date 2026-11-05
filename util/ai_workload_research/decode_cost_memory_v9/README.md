# V9 execution and CPU analysis
Frozen execution sources and SHA-256 values are in SCIENCE_CONTRACT.json. Do not rerun supervisor.py: the sole GPU window ended with a resource STOP.

analyze_curve.py rechecks actual private prompt/output IDs and all public journal hashes, generates CURVE_ANALYSIS.json and FORMAL_SAMPLES.tsv. It accepts the lossless gzip journals. Requires lawful access to the indexed private completion records and V8 minimal references.

analyze_trace.py reads the retained private NSYS SQLite and public NCU base-unit CSV, exports selected full activity tables and produces the core timeline/counter analysis. Extra reported CPU API group/dense-group aggregation and parsed counter scalars were independently calculated after this core analysis; augment_analysis.py reproduces these additions. Neither script initializes CUDA.

Full profiler binaries and private completions stay on109; PRIVATE_RAW_INDEX.json and RAW_ARCHIVE_INDEX.json bind exact bytes. No numerical-boundary GPU task was executed. Sparse observer code/test is a planned altered path, not a native numerical finding.
