# Wave-1 native catalog schema

`native_catalog.py` publishes only small, hash-listed TSV summaries after real G0/G1 runs. A Wave-1 declaration must contain exactly the four frozen deployments (Llama3.2-1B, Qwen2.5-0.5B, Qwen2.5-7B raw, Qwen2.5-7B AWQ), each `COMPLETE` or an explicit `GAP`.

For every `COMPLETE` deployment the validator requires at least three retained `UNPROFILED` `NATIVE_BASELINE` measurements and a `NATIVE_PROFILED` kernel catalog with closed model/tokenizer/input/run identity. Mock/fixture rows are rejected. Raw profiler databases and NVBit traces are never published by this tool.
